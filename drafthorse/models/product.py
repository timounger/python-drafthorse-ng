from . import COMFORT, EXTENDED, NS_RAM
from .container import Container, IDContainer, StringContainer
from .elements import Element
from .party import ManufacturerTradeParty
from .fields import (
    ClassificationField,
    Field,
    IDField,
    MultiField,
    MultiIDField,
    MultiStringField,
    QuantityField,
    StringField,
)


class ProductCharacteristic(Element):
    type_code = StringField(
        NS_RAM,
        "TypeCode",
        required=False,
        profile=EXTENDED,
        _d="Art der Produkteigenschaft",
    )
    description = StringField(NS_RAM, "Description", required=False, profile=COMFORT)
    value_measure = QuantityField(
        NS_RAM,
        "ValueMeasure",
        required=False,
        profile=EXTENDED,
        _d="Numerische Messgröße",
    )
    value = StringField(NS_RAM, "Value", required=False, profile=COMFORT)

    class Meta:
        namespace = NS_RAM
        tag = "ApplicableProductCharacteristic"


class ProductClassification(Element):
    class_code = ClassificationField(
        NS_RAM, "ClassCode", required=False, profile=COMFORT
    )
    value = StringField(NS_RAM, "ClassName", required=False, profile=EXTENDED)

    class Meta:
        namespace = NS_RAM
        tag = "DesignatedProductClassification"


class ProductInstance(Element):
    batch_id = IDField(NS_RAM, "BatchID", required=False, profile=EXTENDED)
    serial_id = StringField(
        NS_RAM, "SupplierAssignedSerialID", required=False, profile=EXTENDED
    )

    class Meta:
        namespace = NS_RAM
        tag = "IndividualTradeProductInstance"


class OriginCountry(Element):
    id = StringField(
        NS_RAM, "ID", required=True, profile=EXTENDED, _d="Land der Produktherkunft"
    )

    class Meta:
        namespace = NS_RAM
        tag = "OriginTradeCountry"


class ReferencedProduct(Element):
    id = IDField(NS_RAM, "ID", required=False, profile=EXTENDED)
    global_id = IDField(NS_RAM, "GlobalID", required=False, profile=EXTENDED)
    further_global_ids: IDContainer = MultiIDField(
        NS_RAM,
        "GlobalID",
        required=False,
        profile=EXTENDED,
        _d="Weitere globale Kennungen",
    )
    seller_assigned_id = StringField(
        NS_RAM, "SellerAssignedID", required=True, profile=EXTENDED
    )
    buyer_assigned_id = StringField(
        NS_RAM, "BuyerAssignedID", required=True, profile=EXTENDED
    )
    industry_assigned_id = IDField(
        NS_RAM, "IndustryAssignedID", required=False, profile=EXTENDED
    )
    name = StringField(NS_RAM, "Name", required=False, profile=EXTENDED)
    description = StringField(NS_RAM, "Description", required=False, profile=EXTENDED)
    unit_quantity = QuantityField(
        NS_RAM, "UnitQuantity", required=False, profile=EXTENDED
    )

    class Meta:
        namespace = NS_RAM
        tag = "IncludedReferencedProduct"


class TradeProduct(Element):
    id = IDField(NS_RAM, "ID", required=False, profile=EXTENDED)
    global_id = IDField(NS_RAM, "GlobalID", required=False)
    seller_assigned_id = IDField(
        NS_RAM, "SellerAssignedID", required=False, profile=COMFORT
    )
    buyer_assigned_id = IDField(
        NS_RAM, "BuyerAssignedID", required=False, profile=COMFORT
    )
    industry_assigned_id = IDField(
        NS_RAM, "IndustryAssignedID", required=False, profile=EXTENDED
    )
    model_id = IDField(NS_RAM, "ModelID", required=False, profile=EXTENDED)
    name = StringField(NS_RAM, "Name", required=False)
    description = StringField(NS_RAM, "Description", required=False, profile=COMFORT)
    batch_id = IDField(NS_RAM, "BatchID", required=False, profile=EXTENDED)
    further_batch_ids: StringContainer = MultiStringField(
        NS_RAM,
        "BatchID",
        required=False,
        profile=EXTENDED,
        _d="Weitere Chargennummern",
    )
    brand_name = StringField(NS_RAM, "BrandName", required=False, profile=EXTENDED)
    model_name = StringField(NS_RAM, "ModelName", required=False, profile=EXTENDED)
    characteristics: Container = MultiField(
        ProductCharacteristic, required=False, profile=COMFORT
    )
    classifications: Container = MultiField(
        ProductClassification, required=False, profile=COMFORT
    )
    instance: Container = MultiField(ProductInstance, required=False, profile=EXTENDED)
    origin: OriginCountry = Field(OriginCountry, required=False, profile=COMFORT)
    manufacturer: ManufacturerTradeParty = Field(
        ManufacturerTradeParty,
        required=False,
        profile=EXTENDED,
        _d="Hersteller des Produkts",
    )
    included_products: Container = MultiField(
        ReferencedProduct, required=False, profile=EXTENDED
    )

    class Meta:
        namespace = NS_RAM
        tag = "SpecifiedTradeProduct"
