from transbank.webpay.webpay_plus.transaction import Transaction
from transbank.common.options import WebpayOptions
from transbank.common.integration_type import IntegrationType

# Configuración de Webpay para pruebas
webpay_transaction = Transaction(
    options=WebpayOptions(
        commerce_code="597055555532",
        api_key="579B532A7440BB0C9079DED94D31EA1615BACEB56610332264630D42D0A36B1C",
        integration_type=IntegrationType.TEST
    )
)
