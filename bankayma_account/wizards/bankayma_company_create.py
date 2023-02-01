# Copyright 2023 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import base64
import csv
import io
import logging

from odoo import _, exceptions, fields, models

_logger = logging.getLogger(__name__)


class BankaymaCompanyCreate(models.TransientModel):
    _name = "bankayma.company.create"
    _description = "Create companies in bulk"

    template_company_id = fields.Many2one(
        "res.company",
        default=lambda self: self.env.company,
        string="Template company",
    )
    user_file = fields.Binary("Users")

    def action_create(self):
        self.ensure_one()

        if not self.env.user.has_group("base.group_system"):
            raise exceptions.AccessError(_("Only admin can cascade companies"))

        if not self.template_company_id.chart_template_id:
            raise exceptions.UserError(
                _(
                    "You need to have configured a chart of accounts for your parent "
                    "company before cloning it"
                )
            )

        new_companies = {}
        import_file = csv.reader(
            io.StringIO(base64.b64decode(self.user_file).decode("utf8"))
        )
        next(import_file)
        next(import_file)
        next(import_file)
        for line in import_file:
            if not line[1]:
                _logger.error("Company %s has no name, ignoring", line[0])
                continue
            company = new_companies.get(line[0])
            if not company:
                company = new_companies[line[0]] = self.sudo()._create_company(
                    self.template_company_id,
                    line[1],
                    line[0],
                )
                _logger.info("Created company %s", company.name)
            if not line[5]:
                _logger.error("No email for %s - not creating user", line[0] or line[1])
                continue
            existing_user = (
                self.env["res.users"]
                .sudo()
                .search([("login", "=", line[3] or line[5])])
            )
            if existing_user:
                existing_user.company_ids += company
                _logger.info(
                    "Added user %s to company %s", existing_user.login, company.name
                )
            else:
                self.env["res.users"].with_context(
                    # don't invite users for now
                    no_reset_password=True,
                ).sudo().create(
                    {
                        "name": line[4] or line[3] or line[5],
                        "login": line[3] or line[5],
                        "email": line[5],
                        "phone": line[6],
                        "function": line[2],
                        "company_id": company.id,
                        "company_ids": [(6, False, company.ids)],
                    }
                )
                _logger.info("Created user %s for company %s", line[4], company.name)

    def _create_company(self, template, name, code):
        """Duplicate template to name, while duplicating accounts/journals"""
        new_company = (
            self.env["res.company"]
            .sudo()
            .create(
                {
                    "name": name,
                    "parent_id": template.id,
                    "country_id": template.country_id.id,
                    "code": code,
                    "company_cascade_from_parent": True,
                }
            )
        )

        for model in (
            "account.account",
            "account.journal",
            "account.payment.mode",
            "account.tax",
            "account.fiscal.position",
            "account.fiscal.position.tax",
        ):
            for record in self.env[model].search([("company_id", "=", template.id)]):
                record._company_cascade()

        fields = [
            field_name
            for field_name, field in template._fields.items()
            if not (
                field_name
                in (
                    tuple(models.MAGIC_COLUMNS)
                    + template._company_cascade_exclude_fields
                )
                or field.related
                or field.compute
                or "prefix" in field_name
            )
        ]
        vals = template._company_cascade_values(
            new_company, template.read(fields, load="_classic_write")[0]
        )

        new_company.write(vals)

        self.env["ir.property"].search([("company_id", "=", new_company.id)]).unlink()
        for prop in self.env["ir.property"].search([("company_id", "=", template.id)]):
            prop._company_cascade()

        return new_company
