from .company import company_register, edit_company
from .supplier import (
    supplier_register,
    supplier_list,
    supplier_profile,
    edit_supplier,
    delete_supplier_confirm,
    delete_supplier
)
from .measurement import (
    measurement_register,
    measurement_list,
    delete_measurement,
    delete_measurement_confirm
)
from .product_category import (
    product_category_register,
    product_category_list,
    delete_product_category,
    delete_product_category_confirm
)
from .vat_rate import (
    vat_rate_register,
    vat_rate_list,
    delete_vat_rate,
    delete_vat_rate_confirm
)
from .product import (
    product_register,
    edit_product,
    product_list,
    delete_product,
    delete_product_confirm,
    get_company_options
)

__all__ = [
    # Company views
    'company_register',
    'edit_company',
    # Supplier views
    'supplier_register',
    'supplier_list',
    'supplier_profile',
    'edit_supplier',
    'delete_supplier_confirm',
    'delete_supplier',
    # Measurement views
    'measurement_register',
    'measurement_list',
    'delete_measurement',
    'delete_measurement_confirm',
    # Product category views
    'product_category_register',
    'product_category_list',
    'delete_product_category',
    'delete_product_category_confirm',
    # VAT rate views
    'vat_rate_register',
    'vat_rate_list',
    'delete_vat_rate',
    'delete_vat_rate_confirm',
    # Product views
    'product_register',
    'edit_product',
    'product_list',
    'delete_product',
    'delete_product_confirm',
    'get_company_options',
]

