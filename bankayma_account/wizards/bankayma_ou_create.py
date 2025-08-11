# Copyright 2023 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import base64
import csv
import io
import logging

from odoo import _, exceptions, fields, models

_logger = logging.getLogger(__name__)


class BankaymaOuCreate(models.TransientModel):
    _name = "bankayma.ou.create"
    _description = "Create OUs in bulk"

    template_operating_unit_id = fields.Many2one(
        "operating.unit",
        default=lambda self: self.env.ref("operating_unit.main_operating_unit"),
        string="Template OU",
        domain=[("parent_id", "=", False)],
    )
    user_file = fields.Binary("Users")
    ou_code = fields.Char()
    ou_name = fields.Char()
    user_function = fields.Char()
    user_login = fields.Char()
    user_name = fields.Char()
    user_email = fields.Char()
    user_phone = fields.Char()

    def action_create(self):
        self.ensure_one()

        if not self.env.user.has_group("base.group_system"):
            raise exceptions.AccessError(_("Only admin can cascade companies"))

        if self.user_file:
            import_file = csv.reader(
                io.StringIO(base64.b64decode(self.user_file).decode("utf8"))
            )
            next(import_file)
            next(import_file)
            next(import_file)
            for line in import_file:
                self.sudo()._create_ou_and_user(*line)
        else:
            self.sudo()._create_ou_and_user(
                self.ou_code,
                self.ou_name,
                self.user_function,
                self.user_login,
                self.user_name,
                self.user_email,
                self.user_phone,
            )

    def _create_ou_and_user(
        self,
        ou_code,
        ou_name,
        user_function,
        user_login,
        user_name,
        user_email,
        user_phone,
    ):
        if not ou_name:
            _logger.error("OU %s has no name, ignoring", ou_code)
            return self.env["operating.unit"]
        ou = self.env["operating.unit"].search([("code", "=", ou_code)])
        if not ou:
            ou = self._create_ou(
                self.template_operating_unit_id,
                ou_name,
                ou_code,
            )
            _logger.info("Created OU %s", ou.name)
        if not user_email:
            _logger.error("No email for %s - not creating user", ou_code or ou_name)
            return self.env["operating.unit"]
        existing_user = self.env["res.users"].search(
            [("login", "=", user_login or user_email)]
        )
        if existing_user:
            existing_user.operating_unit_ids += ou
            _logger.info("Added user %s to OU %s", existing_user.login, ou.name)
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
                        "operating_unit_ids": [fields.Command.set(ou.ids)],
                    }
                )
            )
            _logger.info("Created user %s for OU %s", user.login, ou.name)
        return ou

    def _create_ou(self, template, name, code):
        """Duplicate template to name, while duplicating accounts/journals"""
        new_ou = self.env["operating.unit"].create(
            {
                "name": name,
                "parent_id": template.id,
                "code": code,
                "partner_id": self.env["res.partner"]
                .create(
                    {
                        "name": name,
                        "country_id": template.partner_id.country_id.id,
                    }
                )
                .id,
            }
        )

        return new_ou
