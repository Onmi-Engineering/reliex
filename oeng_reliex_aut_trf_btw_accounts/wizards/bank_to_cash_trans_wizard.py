from odoo import models, fields, api
from odoo.exceptions import UserError


class BankToCashTransferWizard(models.TransientModel):
    _name = 'bank.to.cash.transfer.wizard'
    _description = 'Wizard para Traspaso de Banco a Diario Efectivo'

    journal_id = fields.Many2one('account.journal',
                                 domain="[('bank_statements_source', '!=', 'online_sync'), ('type', 'in', ('bank', 'cash'))]",
                                 string='Diario',
                                 required=True)

    # @api.onchange('journal_id')
    # def _onchange_journal_id(self):
    #     if self.journal_id and self.journal_id.type in ['cash',
    #                                                     'bank'] and self.journal_id.bank_statements_source == 'online_sync':
    #         self.journal_id = False
    #         return {
    #             'warning': {
    #                 'title': 'Error en Diario',
    #                 'message': 'No puedes seleccionar un diario con sincronización en línea habilitada para tipos "Efectivo" o "Banco".',
    #             }
    #         }

    def transfer_to_cash(self):
        active_id = self.env.context.get('active_id')
        if not active_id:
            return

        bank_statement_line = self.env['account.bank.statement.line'].browse(active_id)

        liquidity_account = self.env['res.config.settings'].sudo().search([], limit=1).transfer_account_id

        if not liquidity_account:
            raise UserError("No se encuentra la cuenta de transferencia interna en la configuración.")

        # Modifico el asiento existente obteniendo el asiento contable asociado a la línea de extracto bancario
        move = bank_statement_line.move_id

        if not move:
            raise UserError("No se encontró un asiento contable asociado al extracto bancario.")

        # Dentro del asiento busco la cuenta transitoria 572001
        # transitory_account = self.env['account.journal'].sudo().search([], limit=1).suspense_account_id
        transitory_account = self.journal_id.suspense_account_id

        if not liquidity_account:
            raise UserError("No se encuentra la cuenta de transitorio para el diario.")

        if transitory_account:
            # Filtro las líneas contables que tienen la cuenta transitoria 572001
            transitory_lines = move.line_ids.filtered(lambda line: line.account_id == transitory_account)

            if transitory_lines:
                # Reemplazo la cuenta 572001 por la cuenta de liquidez 5729991
                transitory_lines.write({'account_id': liquidity_account.id})
            else:
                raise UserError("No se encontraron líneas contables con la cuenta transitoria (572001) en el asiento.")
        else:
            raise UserError("No se encuentra la cuenta transitoria (572001).")

        # Si es necesario, publico el asiento (esto depende de si el asiento estaba en borrador o ya estaba publicado)
        if move.state == 'draft':
            move.action_post()

        # Creo un registro en el diario de efectivo, busco el diario de efectivo seleccionado
        cash_journal = self.journal_id

        # Busco un estado de cuenta abierto en el diario de efectivo
        cash_statement = self.env['account.bank.statement'].search([
            ('journal_id', '=', cash_journal.id)
            # ('state', '=', 'open')
        ], limit=1)

        # Si no existe un estado de cuenta abierto, creo uno nuevo
        if not cash_statement:
            cash_statement = self.env['account.bank.statement'].create({
                'journal_id': cash_journal.id,
                'date': fields.Date.today(),
                'name': f'Efectivo {fields.Date.today()}',
            })

        # Crear la línea en el estado de cuenta del diario de efectivo
        cash_statement_line = self.env['account.bank.statement.line'].create({
            'statement_id': cash_statement.id,
            # 'date': fields.Date.today(),
            'date': bank_statement_line.date,
            'amount': -bank_statement_line.amount,  # Reflejar la entrada de efectivo

        })

        # Identificar el asiento contable generado y reemplazar la cuenta 572001 por 5729991
        if cash_statement_line.move_id:
            # transitory_account = self.env['account.account'].search([('code', '=', '572001')], limit=1)
            # transitory_account = self.journal_id.suspense_account_id
            transitory_account = cash_journal.suspense_account_id
            if transitory_account:
                # Filtrar las líneas contables con la cuenta 572001 en el asiento generado
                transitory_lines = cash_statement_line.move_id.line_ids.filtered(
                    lambda line: line.account_id == transitory_account)
                # Reemplazar la cuenta 572001 por 5729991
                transitory_lines.write({'account_id': liquidity_account.id})

        # Filtro las líneas contables con la cuenta de liquidez en el asiento bancario
        bank_liquidity_lines = move.line_ids.filtered(lambda line: line.account_id == liquidity_account)

        # Filtro las líneas contables con la cuenta de liquidez en el asiento generado por la línea del diario de efectivo
        cash_liquidity_lines = cash_statement_line.move_id.line_ids.filtered(
            lambda line: line.account_id == liquidity_account)

        # Concilio las líneas contables de liquidez de ambos diarios
        lines_to_reconcile = bank_liquidity_lines | cash_liquidity_lines
        lines_to_reconcile.reconcile()

