from flask_marshmallow import Marshmallow
from app.__init__ import App

ma = Marshmallow(App.get_app())

class StreamSchema(ma.Schema):
    class Meta:
        fields = ('id','stream_url','stream_type','name')

class PlateSchema(ma.Schema):
    class Meta:
        fields = ('id','plate_number','detected_date','stream_id', 'stream_name')

streams_schema = StreamSchema(many=True)
stream_schema = StreamSchema()

plates_schema = PlateSchema(many=True)