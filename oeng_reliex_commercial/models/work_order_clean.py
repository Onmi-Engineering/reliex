from odoo import fields, models, api, _


class WorkOrderClean(models.Model):
    _inherit = 'work.order.clean'

    @api.depends('establishment_id', 'related_plant_ids')
    def compute_comments_notes(self):
        super(WorkOrderClean, self).compute_comments_notes()
        for rec in self:
            sale_order_text = ''
            extra_note_so = ''
            if rec.lead_id:
                quotation = rec.sudo().lead_id.order_ids.filtered(lambda o: o.state == 'sale')
                if quotation:
                    quotation = quotation[0]
                    i = 1
                    for line in quotation.order_line.filtered(lambda l: l.display_type):
                        sale_order_text += (f"<strong>"
                                            f"     Sección {i}"
                                            f"</strong>"
                                            f"<p>"
                                            f"     {line.name}"
                                            f"</p>")
                        i += 1
                    if quotation.comments_notes:
                        extra_note_so = (f"<strong>"
                                         f"     Observaciones para trabajador/a:"
                                         f"</strong>"
                                         f"<p>"
                                         f"     {quotation.comments_notes}"
                                         f"</p>")
                    else:
                        extra_note_so = ''

            establishment_text = (f"<strong>"
                                  f"     Establecimiento:"
                                  f"</strong>"
                                  f"")
            if rec.establishment_id.comment:
                establishment_text += (f"<p>"
                                       f"   {rec.establishment_id.comment}"
                                       f"</p>"
                                       f"<br/>")
            plant_text = (f"<strong>"
                          f"    Instalaciones:"
                          f"</strong>"
                          f"<br/>"
                          f"<ul>")
            for plant in rec.related_plant_ids:
                plant_text += f"<li>"
                plant_text += (f"<strong>"
                               f"   ○ Instalación - {plant.name}:"
                               f"</strong>")
                if plant.comment:
                    plant_text += (f"<p>"
                                   f"   {plant.comment}"
                                   f"</p>")
                for cooker in plant.cooker_hood_ids:
                    if cooker.cooker_comments:
                        plant_text += (f"<strong>"
                                       f"    • Campana {cooker.name}:"
                                       f"</strong>"
                                       f"<br/>"
                                       f"<p>"
                                       f"{cooker.cooker_comments}"
                                       f"</p>")
                    if cooker.duct_comments:
                        plant_text += (f"<strong>"
                                       f"       • Conducto:"
                                       f"</strong>"
                                       f"<br/>"
                                       f"<p>"
                                       f"{cooker.duct_comments}"
                                       f"</p>")
                    if cooker.extractor_comments:
                        plant_text += (f"   <strong>"
                                       f"       • Extractor:"
                                       f"   </strong>"
                                       f"<br/>"
                                       f"   <p>"
                                       f"       {cooker.extractor_comments}"
                                       f"   </p>")
                    if cooker.filtronic_comments:
                        plant_text += (f"   <strong>"
                                       f"       • Filtronic:"
                                       f"   </strong>"
                                       f"<br/>"
                                       f"   <p>"
                                       f"       {cooker.filtronic_comments}"
                                       f"   </p>")
                plant_text += (f"</li>"
                               f"<br/>")
            plant_text += "</ul>"
            rec.comments_notes = extra_note_so + sale_order_text + establishment_text + plant_text
