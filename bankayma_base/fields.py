from odoo import fields


class TranslatedComputedChar(fields.Char):
    """
    A stored char field that is translatable and computed
    """

    def __init__(self, **kwargs):
        super().__init__(translate=True, store=True, **kwargs)

    def compute_value(self, records):
        result = super().compute_value(records)

        langs = {code for code, _dummy in records.env["res.lang"].get_installed()} - {
            records.env.lang or "en_US"
        }
        for lang in langs:
            records_with_lang = records.with_context(lang=lang)
            super().compute_value(records_with_lang)

        return result
