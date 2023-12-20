from marshmallow import Schema, fields


class LocationSchema(Schema):
    id = fields.Str(dump_only=True)
    destination_name = fields.Str(required=True)
    address = fields.Str(required=True)
    destination_img_url = fields.Str(required=True)
    destination_details = fields.Str(required=True)
    fee = fields.Float()
    category = fields.Str(required=True)
    open_time = fields.Str(required=True)
    rating = fields.Float()
    predict_number = fields.Int()
    link_to_gmaps = fields.Str(required=True)
    createdAt = fields.DateTime()
    updateAt = fields.DateTime()


class LocationUpdateSchema(Schema):
    destination_name = fields.Str(required=True)
    address = fields.Str(required=True)
    destination_img_url = fields.Str(required=True)
    destination_details = fields.Str(required=True)
    fee = fields.Float()
    category = fields.Str(required=True)
    open_time = fields.Str(required=True)
    rating = fields.Float()
    predict_number = fields.Int()
    link_to_gmaps = fields.Str(required=True)
