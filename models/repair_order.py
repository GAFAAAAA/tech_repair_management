import logging
import base64
import qrcode
import os
import re
import uuid
from io import BytesIO
from odoo import models, fields, api
from odoo.tools import config
from odoo.exceptions import ValidationError, UserError
from datetime import timedelta

# Main model for repair management
class RepairOrder(models.Model):
    _name = 'tech.repair.order'
    _inherit = ['mail.thread', 'mail.activity.mixin']  # Enable tracking
    _description = 'Repair Management'
    _order = 'create_date desc'  # Sort by creation date (most recent first)
    _logger = logging.getLogger(__name__)
    
    # Unique repair number, automatically generated
    name = fields.Char(string='Repair Number', required=True, copy=False, default=lambda self: self._generate_sequence())

    # Token
    token_url = fields.Char(string='Token URL', copy=False, readonly=True)


    # Customer associated with the repair
    customer_id = fields.Many2one('res.partner', string='Customer', required=True, context={'from_tech_repair_order': True})
    
    # Multiple devices support
    device_ids = fields.One2many('tech.repair.order.device', 'repair_order_id', string='Devices')
    device_count = fields.Integer(string='Device Count', compute='_compute_device_count', store=True)
    device_summary = fields.Char(string='Devices', compute='_compute_device_summary', store=True)
    
    # Case support for bulk device addition
    temp_case_id = fields.Many2one('tech.repair.case', string='Add from Case', store=False, help="Select a case to add all its devices to this repair order")
    
    # Legacy fields for backward compatibility (deprecated - use device_ids instead)
    # These fields are no longer required to support orders with only device_ids
    category_id = fields.Many2one('tech.repair.device.category', string='Category', required=False)
    brand_id = fields.Many2one('tech.repair.device.brand', string='Brand', required=False)
    model_id = fields.Many2one('tech.repair.device.model', string='Model', required=False)
    variant_id = fields.Many2one('tech.repair.device.variant', string='Variant', domain=[],)



    aesthetic_condition = fields.Selection([
        ('new', 'New'),
        ('good', 'Good'),
        ('used', 'Used'),
        ('damaged', 'Damaged')
        ], string='Aesthetic Condition', default='good')

    # overall device condition at acceptance
    aesthetic_state = fields.Char(string='Visual Defects', required=False , help="If there are visible damages/scratches, write them here")

    # serial / IMEI and with tracking record the changes
    serial_number = fields.Char(string='Serial / IMEI', required=False )

    # SIM code and device password
    sim_pin = fields.Char(string="SIM PIN")
    device_password = fields.Char(string="Device Code/Password")

    # any extra username and password
    credential_ids = fields.One2many(
        'tech.repair.credential', 
        'tech_repair_order_id', 
        string="Credentials"
    )

    # accessories left by the customer
    accessory_ids = fields.One2many(
        'tech.repair.accessory',
        'tech_repair_order_id', 
        string="Accessories",
    )

    # software to install intermediate module
    software_line_ids = fields.One2many(
    'tech.repair.software.line', 
    'repair_order_id', 
    string='Installed Software'
    )

    renewal_softwares = fields.Html(string="Software to Renew", compute="_compute_renewal_softwares")



    # Fictitious State for Online Display
    customer_state_id = fields.Many2one(
        'tech.repair.state.public', 
        string="Customer Visible Status", 
    )

    # External laboratory to which the repair can be sent
    external_lab_ids = fields.One2many(
        'tech.repair.external.lab',
        'tech_repair_order_id',
        string='External Laboratories'
    )

    qr_code = fields.Binary(
        string="Customer QR Code",
        compute="_generate_qr_code",
        store=True
    )
    qr_code_url = fields.Char("QR Code URL", compute="_compute_qr_code_url", store=True)


    qr_code_int = fields.Binary(
        string="Internal QR Code",
        compute="_generate_qr_code_int",
        store=True
    )
    qr_code_int_url = fields.Char("QR Code URL", compute="_compute_qr_code_int_url", store=True)



    # Technician assigned to the repair (employees only) (automated with default user loading the repair)
    assigned_to = fields.Many2one('res.users', string='Assigned to', domain=[('employee', '=', True)], default=lambda self: self.env.user)

    # Technician who opens the repair (employees only) (automated with default user loading the repair) (read only)
    opened_by = fields.Many2one('res.users', string='Opened by', domain=[('employee', '=', True)], default=lambda self: self.env.user, readonly=True)


    # Find the state with sequence = 1 and set it as default
    def _default_state(self):
        state = self.env['tech.repair.state'].search([], order="sequence asc", limit=1)
        return state.id if state else None  # If no states found, return None without errors

    # Repair state, managed dynamically
    # Set the state automatically at creation

    state_id = fields.Many2one(
        'tech.repair.state',
         string='Status', 
         required=True, 
         default=_default_state
        )

    # Description of the problem reported by the customer
    problem_description = fields.Text(
        string='Additional Problem Description',
        help="Problem declared by the customer"
        )

    # Work to be done
    worktype = fields.Many2one(
        'tech.repair.worktype',
        string="Work to be Done",
        required=True
    )

    # Operations performed by the technician
    workoperations = fields.Html(
        string="Operations Performed",
        translate=True,
        sanitize=False,  # Allows HTML without restrictions (can be useful if you want buttons or special formatting)
        sanitize_attributes=False,
        help="Enter operations and use '/' for commands.",
        default="""
        <ul class="o_checklist">
          <li>Office License Checked</li>
          <li>Antivirus License Checked</li>
          <li>Sticker Applied</li>
          <li>Cleaning Performed</li>
        </ul><br/>
        """,
        )

    # Repair cost
    tech_repair_cost = fields.Float(string='Repair Cost €', default=0.0)
    # Down payment made by the customer
    advance_payment = fields.Float(
        string='Down Payment €', 
        default=0.0,
        help="Down payment"
        )
    # Discount
    discount_amount = fields.Float(
        string="Discount €",
        help="Discount amount to apply to the total."
    )

    # Automatic calculation of expected total
    expected_total = fields.Float(string='Expected Total €', compute='_compute_expected_total')
    # Components used for the repair, taken from the warehouse
    components_ids = fields.One2many(
        'tech.repair.component',
        'repair_order_id',
        string='Components Used'
    )

    # Loaner device temporarily assigned to the customer
    loaner_device_id = fields.Many2one(
    'tech.repair.loaner_device', 
    string='Loaner Device',
    domain="[('status', '=', 'available')]",  # Show only available ones
    
    )


    # Opening date (automatically set at creation)
    open_date = fields.Datetime(string='Opening Date', default=lambda self: fields.Datetime.now(), readonly=True)


    # Closing date as computed field
    close_date = fields.Datetime(
        string='Closing Date',
        compute='_compute_close_date',
        store=True
    )

    last_modified_date = fields.Datetime(
    string="Last Modified",
    readonly=True
    )

    stimated_date = fields.Date(
    string="Estimated Delivery Date",
    readonly=True,
    compute='_compute_stimated_date'
    )

    renewal_date = fields.Date(string="Renewal Date", compute="_compute_renewal_date", store=True, tracking=True)  # Job expiration date

    reminder_sent = fields.Boolean(string="Reminder Sent", default=False, copy=False) # expiration emails sent or not

    chat_message_ids = fields.One2many(
        'tech.repair.chat.message',
        'tech_repair_order_id',
        string="Chat Messages"
    )

    new_message = fields.Text(string="New Message", store=False)
    new_message_is_customer = fields.Boolean(string="Visible to Customer", store=False, default=False)

    # Customer's digital signature for repair confirmation
    signature = fields.Binary(string='Customer Signature')
    signature_locked = fields.Boolean(string="Signature Locked", default=True)

    signature_url = fields.Char("Customer Signature URL", compute="_compute_signature_url", store=True)

    # Find the default terms
    def _default_term(self):
        term = self.env['tech.repair.term'].search([('predefinita', '=', True)], limit=1)
        return term.id if term else None  # If no terms found, return None without errors

    term_id = fields.Many2one(
        'tech.repair.term',
        string="Terms",
        help="Select the terms to attach to the repair.",
        default=_default_term
    )

    company_id = fields.Many2one(
        'res.company',
        string="Company",
        required=True,
        default=lambda self: self.env.company
    )

    
    
    # ------ CHATTER ------------

    message_ids = fields.One2many(
        'mail.message', 'res_id',
        domain=lambda self: [('model', '=', self._name)],
        string='Chatter Messages'
    )

    message_follower_ids = fields.One2many(
        'mail.followers', 'res_id',
        domain=lambda self: [('res_model', '=', self._name)],
        string='Followers'
    )

    active = fields.Boolean(default=True, string="Active", help="If unchecked, the job is archived.")

    @api.constrains('device_ids', 'category_id', 'brand_id', 'model_id')
    def _check_devices(self):
        """Ensure either device_ids or legacy device fields are filled"""
        for record in self:
            has_devices = bool(record.device_ids)
            has_legacy = bool(record.category_id and record.brand_id and record.model_id)
            if not has_devices and not has_legacy:
                raise ValidationError("Please add at least one device or fill in the device information fields.")

    @api.depends('device_ids')
    def _compute_device_count(self):
        """Compute the number of devices in the repair order"""
        for record in self:
            record.device_count = len(record.device_ids)

    @api.depends('device_ids', 'device_ids.name', 'category_id', 'brand_id', 'model_id', 'variant_id')
    def _compute_device_summary(self):
        """Generate a summary of devices for display in list view"""
        for record in self:
            if record.device_ids:
                # Use device lines
                device_names = [device.name for device in record.device_ids]
                if len(device_names) > 2:
                    record.device_summary = f"{', '.join(device_names[:2])} (+{len(device_names) - 2} more)"
                else:
                    record.device_summary = ', '.join(device_names)
            elif record.category_id and record.brand_id and record.model_id:
                # Use legacy fields
                parts = [record.category_id.name, record.brand_id.name, record.model_id.name]
                if record.variant_id:
                    parts.append(record.variant_id)
                record.device_summary = ' '.join(parts)
            else:
                record.device_summary = 'No devices'

    # -------------------------- DEF

    @api.model_create_multi # Allows batch creation
    def create(self, vals_list):

        # Find the default terms
        default_term = self.env['tech.repair.term'].search([('predefinita', '=', True)], limit=1)


        for vals in vals_list:

            # If the 'name' field is not present in the values, we generate an automatic repair number
            if 'name' not in vals or not vals['name']:
                vals['name'] = self.env['ir.sequence'].next_by_code('tech.repair.order') or 'New'

            # Generate the unique token for the repair
            if 'token_url' not in vals:
                vals['token_url'] = str(uuid.uuid4())  # Generate a random token

            # Set the user creating the repair as default assignee
            if 'assigned_to' not in vals:
                vals['assigned_to'] = self.env.uid
            
            # Set the user creating the repair by default
            if 'opened_by' not in vals:
                vals['opened_by'] = self.env.uid

            # Set the opening date to the current date and time
            vals['open_date'] = fields.Datetime.now()

            # Automatically set the default terms
            if 'term_id' not in vals or not vals['term_id']:
                vals['term_id'] = default_term.id if default_term else None
            
            #self._logger.info("Final values for creation: %s", vals)

        return super().create(vals_list)
        

    def write(self, vals):
        # Record the date of the last modification
        if 'last_modified_date' not in vals:  # Avoid infinite loop by updating only if not already present
            vals['last_modified_date'] = fields.Datetime.now()

        if 'stimated_date' not in vals:
            print('does not exist!')

        # List of fields to exclude from tracking
        excluded_fields = ['signature','last_modified_date']  # Variable for fields to exclude

        # Get readable field labels
        field_labels = self.fields_get()
        old_expected_totals = {}
        for record in self:
            old_values = {
                field: record[field] 
                for field in vals.keys() 
                if field in record and field not in excluded_fields  # We exclude some fields
            }
            old_expected_totals[record.id] = record.expected_total
            old_loaner = record.loaner_device_id  # Save the previous loaner
            old_credentials = record.credential_ids  # Save previous credentials
            old_accessories = {acc.id: acc.name for acc in record.accessory_ids} # Save accessories before modification
            old_components = record.components_ids # Save components before mod
            old_software_lines = {line.id: line.software_id.display_name for line in record.software_line_ids} # Save software lines before mod


        res = super(RepairOrder, self).write(vals)  # Save modifications first without causing recursion

        for record in self:
            changed_fields = []

            # Controllo modifiche nei campi standard
            for field, old_value in old_values.items():
                new_value = record[field]

                # Evito il problema del False ➝ xxxx eliminando One2many / Many2one / Many2many
                if isinstance(record._fields[field], (fields.One2many, fields.Many2one, fields.Many2many)):
                    continue

                # Se il campo è Many2one, usa display_name
                if isinstance(old_value, models.Model) and isinstance(new_value, models.Model):
                    old_value = old_value.display_name
                    new_value = new_value.display_name

                # Se il campo è di tipo Selection, mostra la label invece del value
                if isinstance(record._fields[field], fields.Selection):
                    selection_dict = dict(record._fields[field].selection)  # Ottengo {value: label}
                    old_value = selection_dict.get(old_value, old_value)
                    new_value = selection_dict.get(new_value, new_value)

                if old_value != new_value:
                    field_name = field_labels[field]['string'] if field in field_labels else field
                    changed_fields.append(f"<strong>{field_name}</strong>: {old_value} ➝ <strong>{new_value}</strong>")


            new_total = record.expected_total
            old_total = old_expected_totals[record.id]
            if old_total != new_total:
                diff = new_total - old_total
                changed_fields.append(f"<strong>Totale Variato €:</strong> {('+ ' if diff >= 0 else '')}{diff}")

            # Blocco la firma dopo la modifica
            if 'signature' in vals:
                record.signature_locked = True
                #self.write({'signature_locked': True})  

            # Tracciamento modifiche accessori
            if 'accessory_ids' in vals:
                new_accessories = {acc.id: acc.name for acc in record.accessory_ids}

                # Troviamo accessori aggiunti
                added_accessories = [name for acc_id, name in new_accessories.items() if acc_id not in old_accessories]
                if added_accessories:
                    changed_fields.append(f"Aggiunti accessori: <strong>{', '.join(added_accessories)}</strong>")

                # Troviamo accessori rimossi
                removed_accessories = [name for acc_id, name in old_accessories.items() if acc_id not in new_accessories]
                if removed_accessories:
                    changed_fields.append(f"Rimossi accessori: <strong>{', '.join(removed_accessories)}</strong>")

                # Troviamo accessori modificati
                for acc_id, old_name in old_accessories.items():
                    if acc_id in new_accessories and old_name != new_accessories[acc_id]:
                        changed_fields.append(f"Modificato accessorio: <strong>{old_name} ➝ {new_accessories[acc_id]}</strong>")
                    # Se voglio rilevare le modifiche “interne” ai record accessori, devo confrontare i singoli campi
                    # Ad es. se i record già esistenti cambiano nome. In quell caso, devo implementarlo su accessor_id.

            # Tracciamento dello stato del muletto e aggiornamento del campo "Assegnato alla riparazione"
            if 'loaner_device_id' in vals:
                new_loaner = self.env['tech.repair.loaner_device'].browse(vals['loaner_device_id']) if vals['loaner_device_id'] else False

                # Se un nuovo muletto è stato assegnato
                if new_loaner:
                    new_loaner.status = 'assigned'
                    new_loaner.tech_repair_order_id = record.id  # Aggiorna il riferimento alla riparazione
                    changed_fields.append(f"Muletto assegnato: <strong>{new_loaner.name} ({new_loaner.serial_number})</strong>")

                # Se il muletto precedente è stato rimosso
                if old_loaner and old_loaner != new_loaner:
                    old_loaner.status = 'available'
                    old_loaner.tech_repair_order_id = False  # Rimuove il riferimento alla riparazione
                    changed_fields.append(f"Muletto reso disponibile: <strong>{old_loaner.name} ({old_loaner.serial_number})</strong>")

            # Tracciamento delle credenziali
            if 'credential_ids' in vals:
                new_credentials = record.credential_ids

                # Troviamo quali credenziali sono state aggiunte e quali rimosse
                # Se la versione di Odoo 18 dà problemi con l’operatore "-", bisogna usare la logica con .filtered()
                # es.:
                # added_credentials = new_credentials.filtered(lambda cred: cred.id not in old_credentials.ids)
                # removed_credentials = old_credentials.filtered(lambda cred: cred.id not in new_credentials.ids)
                added_credentials = new_credentials - old_credentials
                removed_credentials = old_credentials - new_credentials

                if added_credentials:
                    for cred in added_credentials:
                        service = cred.service_type if cred.service_type != 'other' else f"Altro ({cred.service_other})"
                        changed_fields.append(f"Aggiunta credenziale: <strong>{cred.username} / {cred.password}</strong> per <strong>{service}</strong>")

                if removed_credentials:
                    for cred in removed_credentials:
                        # Controlliamo se il record esiste ancora prima di accedere ai suoi campi
                        if cred.exists():
                            service = cred.service_type if cred.service_type != 'other' else f"Altro ({cred.service_other})"
                            changed_fields.append(f"Rimossa credenziale: <strong>{cred.username}</strong> per <strong>{service}</strong>")


                # Controllo modifiche nelle credenziali esistenti
                for cred in new_credentials:
                    old_cred = old_credentials.filtered(lambda c: c.id == cred.id)
                    if old_cred and len(old_cred) == 1:  # ✅ Evitiamo il problema del singleton
                        if old_cred.username != cred.username:
                            changed_fields.append(f"Modificato Username: <strong>{old_cred.username} ➝ {cred.username}</strong>")
                        if old_cred.password != cred.password:
                            changed_fields.append(f"Modificata Password per {cred.username}")
                        if old_cred.service_type != cred.service_type:
                            changed_fields.append(f"Modificato Servizio: <strong>{old_cred.service_type} ➝ {cred.service_type}</strong>")
                        if old_cred.service_other != cred.service_other and cred.service_type == 'other':
                            changed_fields.append(f"Modificato Servizio Altro: <strong>{old_cred.service_other} ➝ {cred.service_other}</strong>")


            # Controllo modifiche componenti
            if 'components_ids' in vals:
                new_components = record.components_ids
                added_components = new_components - old_components
                removed_components = old_components - new_components

                if added_components:
                    # Recuperiamo i nomi (o qualsiasi info desideri) dal record product.product
                    added_names = [c.product_id.display_name for c in added_components if c.product_id]
                    changed_fields.append(f"Aggiunti componenti: <strong>{', '.join(added_names)}</strong>")
                    

                if removed_components:
                    removed_names = [c.product_id.display_name for c in removed_components if c.product_id]
                    changed_fields.append(
                        f"Rimossi componenti: <strong>{', '.join(removed_names)}</strong>"
                    )

            # Controllo modifiche software
            if 'software_line_ids' in vals:
                # Ottieni le righe software attualmente presenti (dopo il write)
                new_lines = record.software_line_ids
                # Calcola le righe aggiunte: confronto in base agli ID
                added_lines = new_lines.filtered(lambda l: l.id not in old_software_lines)
                if added_lines:
                    added_names = [line.software_id.display_name for line in added_lines]
                    changed_fields.append(
                        f"Aggiunti software: <strong>{', '.join(added_names)}</strong>"
                    )
                
                # Calcola le righe rimosse: gli ID presenti nel dizionario ma non più in record.software_line_ids.ids
                new_line_ids = new_lines.ids
                removed_names = [old_software_lines[line_id] for line_id in old_software_lines if line_id not in new_line_ids]
                if removed_names:
                    changed_fields.append(
                        f"Rimossi software: <strong>{', '.join(removed_names)}</strong>"
                    )
                
                # Verifica eventuali modifiche al flag add_to_sum nelle righe esistenti
                for line in new_lines:
                    old_line = self.env['tech.repair.software.line'].browse(line.id)
                    # Se il record esisteva già (cioè era presente nei dati iniziali)
                    if line.id in old_software_lines:
                        # Qui possiamo controllare il flag; essendo la riga ancora presente, possiamo accedervi
                        if old_line.add_to_sum != line.add_to_sum:
                            if line.add_to_sum:
                                changed_fields.append(
                                    f"Software <strong>{line.software_id.display_name}</strong> aggiunto al totale"
                                )
                            else:
                                changed_fields.append(
                                    f"Software <strong>{line.software_id.display_name}</strong> rimosso dal totale"
                                )


            # Se ci sono modifiche, registro il messaggio nel Chatter
            if changed_fields:
                message = "<strong>Modifiche effettuate:</strong><br/>" + "<br/>".join(changed_fields)
                record.message_post(
                    body=message,
                    message_type="notification",
                    subtype_id=self.env.ref("mail.mt_note").id,  # Attiva il Chatter
                    body_is_html=True  # Permette la formattazione HTML
                )

        return res

    # Prevents deletion of jobs, allowing only archiving.
    def unlink(self):
        raise UserError("Repair jobs cannot be deleted. You can only archive them.")

    def action_archive(self):
    # Archives the job instead of deleting it.
        self.write({'active': False})

    # Method to create an automatic job number
    @api.model
    def _generate_sequence(self):
        # Automatically generates a unique repair number
        return self.env['ir.sequence'].next_by_code('tech.repair.order') or 'New Repair'


    # When a loaner is assigned, change its status to 'Assigned'
    @api.onchange('loaner_device_id')
    def _onchange_loaner_device(self):
        if self.loaner_device_id:
            self.loaner_device_id.status = 'assigned'

    @api.onchange('category_id')
    def _onchange_category_id(self):
        # Svuoto il campo 'model_id' e brand_id quando cambia il 'category_id'
        if self.category_id:
            self.model_id = False
            self.brand_id = False

    @api.onchange('brand_id')
    def _onchange_brand_id(self):
        # Svuoto il campo 'model_id' quando cambia il 'brand_id'
        if self.brand_id:
            self.model_id = False

    @api.onchange('state_id')
    def _onchange_state(self):
        for record in self:
            if record.state_id.is_external_lab:
                # Controlla se esiste almeno una riga di laboratorio esterno
                if not record.external_lab_ids:
                    return {
                        'warning': {
                            'title': 'Attenzione',
                            'message': 'Questo stato richiede un laboratorio esterno!',
                        }
                    }
            # Aggiorno automaticamente lo stato visibile al cliente
            if record.state_id and record.state_id.public_state_id:
                record.customer_state_id = record.state_id.public_state_id
            else:
                record.customer_state_id = False  # Resetta se non c'è un mapping


    @api.depends('worktype')
    def _compute_stimated_date(self):
        if self.worktype.stimated_time:
            today = fields.Date.today()
            days = self.worktype.stimated_time
            next_date = today + timedelta(days=days)
            self.stimated_date = next_date
        else:
            today = fields.Date.today()
            self.stimated_date = False

    @api.depends('state_id')
    def _compute_close_date(self):
        for record in self:
            if record.state_id and record.state_id.is_closed:
                if not record.close_date:
                    record.close_date = fields.Datetime.now()


                    if record.id:  # Assicuro che il record sia già salvato
                        record.message_post(body=f"Stato cambiato a '{record.state_id.name}' e chiuso il {record.close_date.strftime('%Y-%m-%d %H:%M:%S')}.", message_type="notification")
            else:
                if record.close_date:  # Se lo stato non è più chiuso, rimuove la data
                    record.close_date = False
                    if record.id:  # Assicuro che il record sia già salvato
                        record.message_post(body=f"⚠ Stato riaperto. Data di chiusura rimossa.", message_type="notification")
    

    # Genera i QRCode
    @api.depends('name')
    def _generate_qr_code(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        for record in self:
            record.qr_code = self._generate_qr_code_for_url(f"{base_url}/repairstatus/{record.token_url}")
            

    @api.depends('name')
    def _generate_qr_code_int(self):
        # Genera un QR Code con il link diretto alla riparazione
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        for record in self:
            record.qr_code_int = self._generate_qr_code_for_url(f"{base_url}/web#id={record.id}&model=tech.repair.order&view_type=form")
    
    # Genera un QR Code per un URL dato
    def _generate_qr_code_for_url(self, url):
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4
        )
        qr.add_data(url)
        qr.make(fit=True)

        img = qr.make_image(fill='black', back_color='white')
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        return base64.b64encode(buffer.getvalue())
    
    # Genera un URL per i QR Code e la firma sul report che non accetta l'immagine base64
    @api.depends('qr_code')
    def _compute_qr_code_url(self):
        
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
       
        for record in self:
            if record.qr_code:
                record.qr_code_url = f"{base_url}/web/image/{record._name}/{record.id}/qr_code"
            else:
                record.qr_code_url = False

    @api.depends('qr_code_int')
    def _compute_qr_code_int_url(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
      
        for record in self:
            if record.qr_code_int:
                record.qr_code_int_url = f"{base_url}/web/image/{record._name}/{record.id}/qr_code_int"
            else:
                record.qr_code_int_url = False

    @api.depends('signature')
    def _compute_signature_url(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
       
        for record in self:
            if record.signature:
                record.signature_url = f"{base_url}/web/image/{record._name}/{record.id}/signature"


    # Metodo per calcolare il totale previsto sottraendo l'acconto
    @api.depends('tech_repair_cost', 'advance_payment', 'components_ids', 
             'external_lab_ids.customer_cost', 'discount_amount', 'worktype', 'software_line_ids')
    def _compute_expected_total(self):
        for record in self:
            component_cost = sum(record.components_ids.filtered(lambda m: m.add_to_sum).mapped('lst_price'))
            # Somma solo i costi dei lab che devono essere aggiunti al totale
            lab_cost = sum(record.external_lab_ids.filtered(lambda l: l.add_to_sum).mapped('customer_cost')) #
            # Somma solo i costi dei software che devono essere aggiunti al totale
            software_cost = sum(line.software_id.price for line in record.software_line_ids if line.add_to_sum)
            worktype_cost = sum(record.worktype.mapped('price'))
            record.expected_total = (
                record.tech_repair_cost + software_cost + lab_cost + component_cost + worktype_cost
            ) - record.advance_payment - record.discount_amount

    @api.depends('software_line_ids.software_id.duration', 'close_date')
    def _compute_renewal_date(self):
        for record in self:
            if record.software_line_ids and record.close_date:
                # Trova la durata massima tra i software installati
                max_duration = max(int(line.software_id.duration) for line in record.software_line_ids)
                record.renewal_date = record.close_date + timedelta(days=max_duration * 30)
            else:
                record.renewal_date = False

    
    @api.depends('software_line_ids')
    def _compute_renewal_softwares(self):
        for record in self:
            # Filtro le righe dei software che richiedono il rinnovo
            softwares = record.software_line_ids.filtered(lambda l: l.software_id.renewal_required)
            html = "<ul>"
            for line in softwares:
                html += "<li>%s</li>" % (line.software_id.name)
            html += "</ul>"
            record.renewal_softwares = html

    # Controlla le commesse in scadenza e invia un'email di promemoria 1 mese prima
    @api.model
    def check_repair_renewals(self):
        today = fields.Date.today()
        renewal_alert_date = today + timedelta(days=30)  # 1 mese prima della scadenza

        # Trova le commesse con scadenza tra 30 giorni e che non hanno ancora ricevuto il promemoria
        orders_to_renew = self.search([
            ('renewal_date', '=', renewal_alert_date),
            ('customer_id', '!=', False),
            ('reminder_sent', '=', False)
        ])

        mail_template = self.env.ref('tech_repair_management.email_template_repair_renewal')

        for order in orders_to_renew:
            # Invia una mail al cliente
            if mail_template:
                mail_template.send_mail(order.customer_id.id, force_send=True)

            # Crea un'opportunità CRM per il rinnovo della commessa
            self.crm_lead_creation(order)
            
            # Imposta il flag per non inviare nuovamente il promemoria
            order.reminder_sent = True

    # Forza l'invio dell'email di rinnovo al cliente
    def action_force_send_renewal_email(self):
        mail_template = self.env.ref('tech_repair_management.email_template_repair_renewal')

        for record in self:
            if not record.renewal_date:
                raise UserError("No renewal date set.")

            if not record.customer_id.email:
                raise UserError(f"Customer {record.customer_id.name} does not have an email set!")

            if mail_template:

                email_values = {
                    'email_to': record.customer_id.email,
                    'email_from': f"{record.company_id.name} <{record.company_id.email or ''}>", # se vuoto, imposta quello configurato
                }
                
                mail_template.send_mail(record.id, force_send=True, ) # email_values=email_values

                record.message_post(
                    body=f"⚡ Email di rinnovo inviata manualmente a {record.customer_id.email}.",
                    message_type="comment"
                )

                self.crm_lead_creation(record)


    def crm_lead_creation(self, record):
        crm_lead_obj = self.env['crm.lead']
        
        # Cerca se esiste già un lead associato a questa commessa
        existing_lead = crm_lead_obj.search([('repair_order_id', '=', record.id)], limit=1)
        if existing_lead:
            # Se esiste già, puoi decidere di uscire o eventualmente aggiornare il lead esistente
            return

        crm_tag = self.env['crm.tag']
        # Cerca se esiste già l'etichetta "Rinnovi"
        renewal_tag = crm_tag.search([('name', '=', 'Rinnovi')], limit=1)
        if not renewal_tag:
            renewal_tag = crm_tag.create({'name': 'Rinnovi'})

        crm_lead_obj.create({
            'name': f"Rinnovo Software - {record.customer_id.name}",
            'partner_id': record.customer_id.id,
            'repair_order_id': record.id,  # Associa il lead alla commessa
            'type': 'opportunity',
            'tag_ids': [(4, renewal_tag.id)],  # Assegna l'etichetta "Rinnovi"
            'description': f"""
                <p>Rinnovo software della commessa 
                <strong><a href="{self.env['ir.config_parameter'].sudo().get_param('web.base.url')}/web#id={record.id}&model=tech.repair.order&view_type=form">{record.name}</a></strong> 
                per <strong>{record.customer_id.name}</strong>.</p>
                <p><strong>Scadenza:</strong> {record.renewal_date.strftime('%d/%m/%Y') if record.renewal_date else 'Data non disponibile'}</p>
                <p><strong>Mail:</strong> {record.customer_id.email or 'Non disponibile'}</p>
                <p><strong>Software da rinnovare:</strong></p>
                <ul>
                    {"".join([f"<li>{line.software_id.name} - €{line.software_id.price:.2f}</li>" 
                            for line in record.software_line_ids if line.software_id.renewal_required])}
                </ul>
            """,
            'expected_revenue': sum(line.software_id.price for line in record.software_line_ids if line.software_id.renewal_required),
            'probability': 50,
        })


    # Gestione del tasto invia messaggio al cliente online
    def action_send_message(self):
        for record in self:
            if record.new_message:
                self.env['tech.repair.chat.message'].create({
                    'tech_repair_order_id': record.id,
                    'sender': 'technician',
                    'message': record.new_message,
                })

                # Aggiungo il messaggio del tecnico nel Chatter
                record.sudo().message_post(
                    body=f"<strong>Risposta Tecnico:</strong> {record.new_message}",
                    message_type="comment",
                    subtype_xmlid="mail.mt_comment",
                    body_is_html=True  # Permette la formattazione HTML
                )
                record.new_message = ""

    
    # Salva la riparazione e mostra una notifica di conferma
    def action_save_repair(self):
        for record in self:
            record.message_post(body="La riparazione è stata salvata con successo.", message_type="notification")

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Successo!',
                'message': 'Riparazione salvata con successo!',
                'sticky': False,  # Se True, la notifica rimane visibile finché l'utente non la chiude
                'type': 'success',  # Può essere 'success', 'warning', 'danger'
            }
        }
    
    # Azioni per stampare il report della riparazione 
    def action_print_repair_report(self):
        return self.env.ref('tech_repair_management.action_report_repair_order').report_action(self)

    def action_print_repair_two_copies_report(self):
        return self.env.ref('tech_repair_management.action_report_repair_order_two_copies').report_action(self)

    

                

    # Metodo per creare un ordine di vendita manualmente dalle riparazioni
    def action_create_sale_order(self):
        sale_order = self.env['sale.order'].create({
            'partner_id': self.customer_id.id,
            'order_line': [(0, 0, {'product_id': comp.id, 'price_unit': comp.lst_price}) for comp in self.components_ids]
        })
        return sale_order

    # sblocca la firma
    def action_unlock_signature(self):
        self.write({'signature_locked': False})
    
    def action_add_devices_from_case(self):
        """Add all devices from the selected case to the repair order"""
        if not self.temp_case_id:
            raise UserError("Please select a case first.")
        
        # Store case name before clearing
        case_name = self.temp_case_id.name
        
        # Find all devices in the selected case that are available
        devices_in_case = self.env['tech.repair.inventory'].search([
            ('case_id', '=', self.temp_case_id.id),
            ('status', '=', 'available')
        ])
        
        if not devices_in_case:
            raise UserError("No available devices found in the selected case.")
        
        # Update the customer if case has a company
        if self.temp_case_id.company_id:
            self.customer_id = self.temp_case_id.company_id
        
        # Add each device to the repair order
        device_lines = []
        for device in devices_in_case:
            device_lines.append((0, 0, {
                'category_id': device.category_id.id,
                'brand_id': device.brand_id.id,
                'model_id': device.model_id.id,
                'variant_id': device.variant_id.id if device.variant_id else False,
                'inventory_id': device.id,
            }))
        
        self.device_ids = device_lines
        
        # Clear the temporary case selection
        self.temp_case_id = False
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Success!',
                'message': f'{len(devices_in_case)} device(s) added from case {case_name}',
                'sticky': False,
                'type': 'success',
            }
        }
    
    # Ricerca per QRCode
    @api.model
    def search_by_qr(self, qr_code_value):
        # Cerca una riparazione in base al numero scansionato dal QR Code
        return self.search([('name', '=', qr_code_value)], limit=1)
