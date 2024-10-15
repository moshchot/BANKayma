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
        default=lambda self: self.env.ref("base.main_company"),
        string="Template company",
        domain=[("parent_id", "=", False)],
    )
    user_file = fields.Binary("Users")
    company_code = fields.Char()
    company_name = fields.Char()
    user_function = fields.Char()
    user_login = fields.Char()
    user_name = fields.Char()
    user_email = fields.Char()
    user_phone = fields.Char()

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

        if self.user_file:
            import_file = csv.reader(
                io.StringIO(base64.b64decode(self.user_file).decode("utf8"))
            )
            next(import_file)
            next(import_file)
            next(import_file)
            for line in import_file:
                self.sudo()._create_company_and_user(*line)
        else:
            self.sudo()._create_company_and_user(
                self.company_code,
                self.company_name,
                self.user_function,
                self.user_login,
                self.user_name,
                self.user_email,
                self.user_phone,
            )

    def _create_company_and_user(
        self,
        company_code,
        company_name,
        user_function,
        user_login,
        user_name,
        user_email,
        user_phone,
    ):
        if not company_name:
            _logger.error("Company %s has no name, ignoring", company_code)
            return self.env["res.company"]
        company = self.env["res.company"].search([("code", "=", company_code)])
        if not company:
            company = self._create_company(
                self.template_company_id,
                company_name,
                company_code,
            )
            _logger.info("Created company %s", company.name)
        if not user_email:
            _logger.error(
                "No email for %s - not creating user", company_code or company_name
            )
            return self.env["res.company"]
        existing_user = self.env["res.users"].search(
            [("login", "=", user_login or user_email)]
        )
        if existing_user:
            existing_user.company_ids += company
            _logger.info(
                "Added user %s to company %s", existing_user.login, company.name
            )
        else:
            user = (
                self.env["res.users"]
                .with_context(
                    # don't invite users for now
                    no_reset_password=True,
                )
                .create(
                    {
                        "name": user_name or user_login or user_email,
                        "login": user_login or user_email,
                        "email": user_email,
                        "phone": user_phone,
                        "function": user_function,
                        "company_id": company.id,
                        "company_ids": [(6, False, company.ids)],
                    }
                )
            )
            _logger.info("Created user %s for company %s", user.login, company.name)
        return company

    def _create_company(self, template, name, code):
        """Duplicate template to name, while duplicating accounts/journals"""
        new_company = self.env["res.company"].create(
            {
                "name": name,
                "parent_id": template.id,
                "country_id": template.country_id.id,
                "code": code,
                "company_cascade_from_parent": True,
            }
        )

        for model in (
            "ir.sequence",
            "account.account",
            "account.journal",
            "account.payment.mode",
            "account.tax",
            "account.fiscal.position",
            "account.fiscal.position.tax",
        ):
            for record in self.env[model].search([("company_id", "=", template.id)]):
                record.with_context(company_cascade_up=True)._company_cascade()

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

        new_company.with_context(company_cascade_up=True).write(vals)

        self.env["ir.property"].search([("company_id", "=", new_company.id)]).unlink()
        for prop in self.env["ir.property"].search([("company_id", "=", template.id)]):
            prop.with_context(company_cascade_up=True)._company_cascade()

        return new_company
