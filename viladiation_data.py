    db.query(MerchantCountries).filter(MerchantCountries.merchant_id == incoming_data['merchantRef'],MerchantCountries.country_id==incoming_data['country']).first()
    db.query(MerchantCurrency).filter(MerchantCurrency.merchant_id == incoming_data['merchantRef'],MerchantCurrency.currency_id==incoming_data['currencyCode']).first()
    len(incoming_data['address'])>8
    len(incoming_data['fullName'])>8
    "@" in incoming_data['email']
    len(incoming_data['transactionRef'])>10
    len(incoming_data['userRef'])>10
    len(incoming_data['mobileNumber'])>10
db.query(Merchant).filter(Merchant.merchant_referance ==incoming_data['merchantRef']).first()