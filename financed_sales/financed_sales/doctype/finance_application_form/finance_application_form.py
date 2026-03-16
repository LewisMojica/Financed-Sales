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

		a_credito: DF.Currency
		amistad_barrio: DF.Data | None
		amistad_link_mapa: DF.Data | None
		amistad_lugar_trabajo: DF.Data | None
		amistad_nombres: DF.Data | None
		amistad_parentesco: DF.Data | None
		amistad_referencia: DF.Data | None
		amistad_telefono_trabajo: DF.Data | None
		amistad_telefonos: DF.Data | None
		anos_trabajando: DF.Data | None
		articulo: DF.Link | None
		avance_inicial: DF.Currency
		barrio: DF.Data | None
		calle: DF.Data | None
		cantidad: DF.Int
		casa_propia: DF.Check
		codigo: DF.Data | None
		codeudor_anos_trabajando: DF.Data | None
		codeudor_casa_propia: DF.Check
		codeudor_calle: DF.Data | None
		codeudor_cedula: DF.Data | None
		codeudor_hijos: DF.Int
		codeudor_jefe_inmediato: DF.Data | None
		codeudor_link_mapa: DF.Data | None
		codeudor_lugar_trabajo: DF.Data | None
		codeudor_nombres: DF.Data | None
		codeudor_profesion: DF.Data | None
		codeudor_salario: DF.Currency
		codeudor_sector: DF.Data | None
		codeudor_telefono_jefe: DF.Data | None
		codeudor_telefono_trabajo: DF.Data | None
		codeudor_tiempo_en_direccion: DF.Data | None
		comercial1_articulos: DF.Data | None
		comercial1_cuando: DF.Data | None
		comercial1_direccion: DF.Data | None
		comercial1_empresa: DF.Data | None
		comercial1_razon: DF.SmallText | None
		comercial1_telefono: DF.Data | None
		cuotas: DF.Currency
		customer: DF.Link
		dias: DF.Int
		enlace_direccion: DF.Data | None
		esposo_hijos: DF.Int
		esposo_nombres: DF.Data | None
		esposo_salario: DF.Currency
		esposo_telefonos: DF.Data | None
		familiar1_barrio: DF.Data | None
		familiar1_link_mapa: DF.Data | None
		familiar1_lugar_trabajo: DF.Data | None
		familiar1_nombres: DF.Data | None
		familiar1_parentesco: DF.Data | None
		familiar1_referencia: DF.Data | None
		familiar1_telefono_trabajo: DF.Data | None
		familiar1_telefonos: DF.Data | None
		familiar2_barrio: DF.Data | None
		familiar2_link_mapa: DF.Data | None
		familiar2_lugar_trabajo: DF.Data | None
		familiar2_nombres: DF.Data | None
		familiar2_parentesco: DF.Data | None
		familiar2_referencia: DF.Data | None
		familiar2_telefono_trabajo: DF.Data | None
		familiar2_telefonos: DF.Data | None
		fecha: DF.Date
		fotos_casa: DF.AttachImage | None
		hijos: DF.Int
		inicial: DF.Currency
		jefe_inmediato: DF.Data | None
		link_mapa_solicitante: DF.Data | None
		lugar_de_trabajo: DF.Data | None
		pagares: DF.Int
		pasaporte_cedula: DF.Data | None
		prestamo_balance: DF.Currency
		prestamo_cuotas: DF.Currency
		prestamo_fecha: DF.Date | None
		prestamo_monto: DF.Currency
		profesion_o_puesto: DF.Data | None
		salario: DF.Currency
		sector: DF.Data | None
		telefono_jefe: DF.Data | None
		telefono_trabajo: DF.Data | None
		tiempo_en_direccion: DF.Data | None
	# end: auto-generated types

	pass
