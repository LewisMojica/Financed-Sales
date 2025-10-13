# Copyright (c) 2025, Lewis Mojica and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class FinanceApplicationForm(Document):
	"""Finance Application Form for credit applications."""
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		amistad_barrio: DF.Data | None
		amistad_lugar_trabajo: DF.Data | None
		amistad_nombres: DF.Data | None
		amistad_parentesco: DF.Data | None
		amistad_referencia: DF.Data | None
		amistad_telefonos: DF.Data | None
		barrio: DF.Data | None
		calle: DF.Data | None
		casa_propia: DF.Check
		codeudor_casa_propia: DF.Check
		codeudor_calle: DF.Data | None
		codeudor_cedula: DF.Data | None
		codeudor_hijos: DF.Int
		codeudor_lugar_trabajo: DF.Data | None
		codeudor_nombres: DF.Data | None
		codeudor_profesion: DF.Data | None
		codeudor_sector: DF.Data | None
		comercial1_cuando: DF.Data | None
		comercial1_donde: DF.Data | None
		comercial1_empresa: DF.Data | None
		comercial1_incautado: DF.Data | None
		comercial1_razon: DF.SmallText | None
		comercial1_telefono: DF.Data | None
		comercial2_cuando: DF.Data | None
		comercial2_donde: DF.Data | None
		comercial2_empresa: DF.Data | None
		comercial2_incautado: DF.Data | None
		comercial2_razon: DF.SmallText | None
		comercial2_telefono: DF.Data | None
		customer: DF.Link
		esposo_hijos: DF.Int
		esposo_nombres: DF.Data | None
		esposo_telefonos: DF.Data | None
		familiar1_barrio: DF.Data | None
		familiar1_lugar_trabajo: DF.Data | None
		familiar1_nombres: DF.Data | None
		familiar1_parentesco: DF.Data | None
		familiar1_referencia: DF.Data | None
		familiar1_telefono_trabajo: DF.Data | None
		familiar1_telefonos: DF.Data | None
		familiar2_barrio: DF.Data | None
		familiar2_lugar_trabajo: DF.Data | None
		familiar2_nombres: DF.Data | None
		familiar2_parentesco: DF.Data | None
		familiar2_referencia: DF.Data | None
		familiar2_telefonos: DF.Data | None
		fecha: DF.Date
		hijos: DF.Int
		jefe_inmediato: DF.Data | None
		lugar_de_trabajo: DF.Data | None
		pasaporte_cedula: DF.Data | None
		prestamo_balance: DF.Currency
		prestamo_cuotas: DF.Currency
		prestamo_fecha: DF.Date | None
		prestamo_monto: DF.Currency
		profesion_o_puesto: DF.Data | None
		sector: DF.Data | None
	# end: auto-generated types

	pass
