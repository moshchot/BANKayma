from urllib.parse import urlparse, urlunparse

from odoo import api, fields, models, tools


class BankaymaProjectPageEmbedCode(models.TransientModel):
    _name = "bankayma.project.page.embed.code"
    _description = "Generate embedding code for project page"
    _rec_name = "operating_unit_id"

    operating_unit_id = fields.Many2one("operating.unit")
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
                    self.operating_unit_id.website_link + "/embed",
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
    display_name = fields.Char(
        compute="_compute_display_name", search="_search_display_name"
    )
    name = fields.Char()
    value = fields.Char()

    def _get_options(self):
        view = (
            self.env.ref("bankayma_website.project_page_embed")
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
    ):
        query = tools.Query(self.env, "dummy")
        query._ids = [_id for _id, _dummy in self._get_options()]
        return query

    def _fetch_query(self, query, fields):
        options = dict(self._get_options())
        for _id in query._ids:
            this = self.browse(_id)
            for field in fields:
                self.env.cache.insert_missing(this, field, (options[this.id],))
        return self.browse(query)
