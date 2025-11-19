from odoo import http
from odoo.http import request
import logging


class RepairController(http.Controller):
    _inherit = ['mail.channel']

    _logger = logging.getLogger(__name__)

    # public string to display the job
    @http.route('/repairstatus/<string:token>', type='http', auth="public", website=True)
    def tech_repair_status(self, token, **kwargs):
        # Force Odoo to use a db
        db_name = request.httprequest.args.get('db')
        if db_name:
            request.session.db = db_name
            
        tech_repair_order = request.env['tech.repair.order'].sudo().search([('token_url', '=', token)], limit=1)

        # Filter only messages for the customer
        chat_messages = request.env['tech.repair.chat.message'].sudo().search([
            ('tech_repair_order_id.token_url', '=', token)
        ], order='create_date asc')

        # Debug log
        #self._logger.info("Messages found for repair %s: %s", token, chat_messages)

        return request.render('tech_repair_management.tech_repair_status_page', {
            'repair': tech_repair_order,
            'customer_state': tech_repair_order.customer_state_id.name if tech_repair_order.customer_state_id else "Status not yet available",
            'open_date': tech_repair_order.open_date.strftime('%d/%m/%Y %H:%M') if tech_repair_order.open_date else "Date not available",
            'last_modified_date': tech_repair_order.last_modified_date.strftime('%d/%m/%Y %H:%M') if tech_repair_order.last_modified_date else "Date not available",
            'chat_messages': chat_messages,
        })

    # public string to send messages
    @http.route('/repairstatus/send_message', type='http', auth="public", methods=['POST'], website=True)
    def send_message(self, **post):
        token = post.get('token')
        customer_message = post.get('customer_message')  # Correct field name from form

        if token and customer_message:
            tech_repair_order = request.env['tech.repair.order'].sudo().search([('token_url', '=', token)], limit=1)
            if tech_repair_order.exists():
                # Save the message in the `tech.repair.chat.message` table
                request.env['tech.repair.chat.message'].sudo().create({
                    'tech_repair_order_id': tech_repair_order.id,
                    'sender': 'customer',  # Indicate that it's a customer message
                    'message': customer_message
                })

                # Add the message to Chatter
                tech_repair_order.message_post(
                    body=f"<strong>Message from Customer:</strong> {customer_message}",
                    message_type="comment",
                    subtype_xmlid="mail.mt_comment",
                    body_is_html=True  # Allows HTML formatting
                )

        return request.redirect(f'/repairstatus/{token}')



    # public string to generate pdf via token
    @http.route('/repairstatus/pdf/<string:token>', type='http', auth="public", website=True)
    def download_repair_pdf(self, token, **kwargs):
        
        repair_order = request.env['tech.repair.order'].sudo().search([('token_url', '=', token)], limit=1)

        if not repair_order.exists():
            #self._logger.error(f"No repair found for token: {token}")
            return request.not_found()

        #self._logger.info(f"Repair found - ID: {repair_order.id}, Name: {repair_order.name}")

        # Retrieve Odoo report
        report_action = request.env.ref('tech_repair_management.action_report_repair_order', raise_if_not_found=False)
        if not report_action:
            #self._logger.error("Error: Report does not exist in Odoo")
            return request.make_response("Error: Report does not exist.", [('Content-Type', 'text/plain')])

        # Generate PDF with single ID (not a list)
        try:
            # Generate PDF using report name
            pdf_content, content_type = request.env['ir.actions.report']._render_qweb_pdf(
                'tech_repair_management.action_report_repair_order', [repair_order.id]
            )
            #self._logger.info(f"PDF generated successfully for ID: {repair_order.id}")

        except Exception as e:
            #self._logger.error(f"Error generating PDF: {str(e)}")
            return request.make_response(f"Error generating PDF: {str(e)}", [('Content-Type', 'text/plain')])

            # Return PDF as response
        pdf_filename = f"Repair_{repair_order.name}.pdf"
        return request.make_response(pdf_content, [
            ('Content-Type', 'application/pdf'),
            ('Content-Disposition', f'attachment; filename={pdf_filename}')
        ])



    