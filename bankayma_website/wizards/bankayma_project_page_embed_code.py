from urllib.parse import urlparse, urlunparse

from odoo import api, fields, models


class BankaymaProjectPageEmbedCode(models.TransientModel):
    _name = "bankayma.project.page.embed.code"
    _description = "Generate embedding code for project page"
    _rec_name = "company_id"

    company_id = fields.Many2one("res.company")
    options = fields.Many2many(
        "bankayma.project.page.embed.code.option",
        compute="_compute_options",
        inverse="_inverse_options",
    )
    embed_code = fields.Text()
    embed_code_html = fields.Html(
        "Preview", compute="_compute_embed_code_html", sanitize=False
    )

    def default_get(self, fields_list):
        result = super().default_get(fields_list)
        result["options"] = (
            self.env["bankayma.project.page.embed.code.option"].search([]).ids
        )
        return result

    def _compute_options(self):
        for this in self:
            this.options = self.env["bankayma.project.page.embed.code.option"].browse()

    @api.depends("embed_code")
    def _compute_embed_code_html(self):
        for this in self:
            this.embed_code_html = this.embed_code

    def _inverse_options(self):
        pass

    @api.onchange("options")
    def _onchange_options(self):
        base_url = urlparse(
            self.env["ir.config_parameter"].sudo().get_param("web.base.url")
        )
        options = "&".join(f"{option.name}=1" for option in self.options)
        html = '<iframe src="{}" style="border: none; width: 100%; height: 100%" />'
        self.embed_code = html.format(
            urlunparse(
                (
                    "",
                    base_url.netloc,
                    self.company_id.website_link + "/embed",
                    "",
                    options,
                    "",
                )
            )
        )


class BankaymaProjectPageEmbedCodeLine(models.AbstractModel):
    _name = "bankayma.project.page.embed.code.option"
    _description = "Embedding option"

    id = fields.Id()
    name = fields.Char()
    value = fields.Char()

    def _get_options(self):
        view = (
            self.env.ref("bankayma_website.company_page_embed")
            .sudo()
            ._get_combined_arch()
        )
        for counter, section in enumerate(
            view.xpath("//section[starts-with(@t-if, 'show_')]")
        ):
            yield counter + 1, section.attrib["t-if"][5:]

    @api.model
    def _search(
        self,
        domain,
        offset=0,
        limit=None,
        order=None,
        count=False,
        access_rights_uid=None,
    ):
        return [_id for _id, _dummy in self._get_options()]

    def _read(self, field_names):
        options = dict(self._get_options())
        for this in self:
            for field_name in field_names:
                self.env.cache.insert_missing(
                    this, self._fields[field_name], (options[this.id],)
                )
