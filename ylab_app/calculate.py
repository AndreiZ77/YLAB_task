# •Базовой валютой называется валюта, относительно которой устанавливается курс для всех остальных валют.
# •Валютой конвертации называется любая другая используемая валюта, в денежные знаки которой конвертируется сумма.
# •Курс валют определяет стоимость валюты конвертации относительно базовой.
# •Кратность указывает, какому количеству денежных единиц базовой валюты соответствует установленный курс.
# [Сумма в валюте конвертации(2)]=[Сумма в валюте конвертации(1)]*[Кратность(1)]*[Курс(2)]/[Кратность(2)]*[Курс(1)]


async def currency_conversion(amount_1, rate_rub_1, multiplier_1, rate_rub_2, multiplier_2):
    return (amount_1 * multiplier_1 * rate_rub_2) / (multiplier_2 * rate_rub_1)
