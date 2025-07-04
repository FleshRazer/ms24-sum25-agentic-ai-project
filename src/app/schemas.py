from typing import List

from pydantic import BaseModel, Field, RootModel


class Item(BaseModel):
    """An item from procurement technical specification."""

    name: str = Field(..., alias="Наименование")
    brand: str | None = Field(..., alias="Марка")
    type: str | None = Field(..., alias="Тип")
    quantity: float | None = Field(..., alias="Количество")
    unit_of_measurement: str | None = Field(..., alias="Единица измерения")
    has_analogues: str | None = Field(
        ..., alias="Наличие аналогов", pattern="^(Да|Нет)$"
    )
    okdp2_code: str | None = Field(..., alias="Код ОКДП2")
    novelty_info: str | None = Field(..., alias="Сведения о новизне")
    application_area: str | None = Field(..., alias="Область применения")
    operating_conditions: str | None = Field(..., alias="Условия эксплуатации")
    technical_requirements: str | None = Field(..., alias="Технические требования")
    configuration: str | None = Field(..., alias="Комплектация")
    acceptance_rules: str | None = Field(
        ..., alias="Требования по правилам сдачи и приемки"
    )
    transportation_requirements: str | None = Field(
        ..., alias="Требования к транспортированию"
    )
    storage_requirements: str | None = Field(..., alias="Требования к хранению")


class ItemList(RootModel):
    """A List of items from procurement technical specification."""

    root: List[Item]
