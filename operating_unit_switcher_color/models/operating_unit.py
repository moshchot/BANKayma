# Copyright 2026 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)
from odoo import fields, models


class OperatingUnit(models.Model):
    _inherit = "operating.unit"

    ou_colors = fields.Serialized()
    color_navbar_bg = fields.Char("Navbar Background Color", sparse="ou_colors")
    color_navbar_bg_hover = fields.Char(
        "Navbar Background Color Hover", sparse="ou_colors"
    )
    color_navbar_border_bottom = fields.Char(
        "Navbar Bottom Border Color", sparse="ou_colors"
    )
    color_navbar_text = fields.Char("Navbar Text Color", sparse="ou_colors")
    color_button_text = fields.Char("Button Text Color", sparse="ou_colors")
    color_button_bg = fields.Char("Button Background Color", sparse="ou_colors")
    color_button_bg_hover = fields.Char(
        "Button Background Color Hover", sparse="ou_colors"
    )
    color_link_text = fields.Char("Link Text Color", sparse="ou_colors")
    color_link_text_hover = fields.Char("Link Text Color Hover", sparse="ou_colors")
    color_submenu_text = fields.Char("Submenu Text Color", sparse="ou_colors")
    scss_modif_timestamp = fields.Char("SCSS Modif. Timestamp")

    def create(self, vals_list):
        result = super().create(vals_list)
        self.scss_create_or_update_attachment()
        return result

    def write(self, vals):
        result = super().write(vals)
        if any(self._fields[field_name].sparse == "ou_colors" for field_name in vals):
            self.scss_create_or_update_attachment()
        return result

    def button_compute_color(self):
        tmp_company = self.env["res.company"].new(
            {
                field_name: self[field_name]
                for field_name, field in self._fields.items()
                if field.sparse == "ou_colors"
            }
        )
        tmp_company.logo = self.partner_id.avatar_512
        ResCompanyClass = tmp_company.__class__
        try:
            ResCompanyClass.write = self.write
            ResCompanyClass.update = self.update
            tmp_company.button_compute_color()
        finally:
            del ResCompanyClass.write
            del ResCompanyClass.update

    def scss_create_or_update_attachment(self):
        css_content = ""
        for this in self.sudo().with_context(allowed_ou_ids=False).search([]):
            company_colors = {
                field_name: this[field_name]
                for field_name, field in self._fields.items()
                if field.sparse == "ou_colors"
            }
            tmp_company = self.env["res.company"].new(
                dict(company_colors=company_colors, **company_colors)
            )
            css_content += f"body[data-ou-id='{this.id}'] {{\n"
            css_content += tmp_company._scss_generate_content()
            css_content += "}\n"
        self.env.ref("operating_unit_switcher_color.attachment_css").write(
            {
                "mimetype": "text/css",
                "raw": css_content or "// empty",
            }
        )
