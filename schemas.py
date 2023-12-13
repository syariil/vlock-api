from marshmallow import Schema, fields


class LocationSchema(Schema):
    id = fields.Str(dump_only=True)
    title = fields.Str(required=True)
    image = fields.Str(required=True)
    description = fields.Str(required=True)
    fee = fields.Float()
    createdAt = fields.DateTime()
    updateAt = fields.DateTime()


class LocationUpdateSchema(Schema):
    title = fields.Str(required=False)
    image = fields.Str(required=False)
    description = fields.Str(required=False)
    fee = fields.Int(required=False)


class UserSchema(Schema):
    id = fields.Int()
    name = fields.Str(required=True)


class PredictionSchema(Schema):
    prediction = fields.List(fields.Str)
