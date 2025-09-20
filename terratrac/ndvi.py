import ee
ee.Initialize(project='terratrac')
from .models import NDVIRecord, ForestArea

class calc_ndvi:
    def __init__(self, lat, long, buffer_size=250):
        lat = float(lat)
        long = float(long)
        self.point = ee.Geometry.Point([long, lat])
        self.buffer = self.point.buffer(buffer_size)

    def mask_cloud(self,img):
        qa = img.select('QA60')
        cloud_mask = qa.bitwiseAnd(1 << 10).eq(0).And( qa.bitwiseAnd(1 << 11).eq(0))
        return img.updateMask(cloud_mask).divide(10000)

    def composite(self, start, end):
        col = (ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
                .filterBounds(self.buffer)
                .filterDate(start, end)
                .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 30))
                .map(self.mask_cloud))
        return col.median()

    def ndvi(self, img):
        ndvi = img.normalizedDifference(['B8', 'B4']).rename('NDVI')
        return ndvi

    def mean_ndvi(self, start, end):
        img = self.composite(start, end)
        ndvi_img = self.ndvi(img)
        mean_dict = ndvi_img.reduceRegion(reducer=ee.Reducer.mean(), geometry=self.buffer, scale=10)
        mean_ndvi = mean_dict.get('NDVI').getInfo()
        return mean_ndvi

    def compare_ndvi(self, start1, end1, start2, end2):
        mean_ndvi1 = self.mean_ndvi(start1, end1)
        mean_ndvi2 = self.mean_ndvi(start2, end2)
        return mean_ndvi1, mean_ndvi2

    def change_detection(self, start1, end1, start2, end2):
        mean_ndvi1 = self.mean_ndvi(start1, end1)
        mean_ndvi2 = self.mean_ndvi(start2, end2)
        change = mean_ndvi2 - mean_ndvi1

        if change < 0:
            return 'Deforestation', change
        elif change > 0:
            return 'Afforestation', change
        else:
            return 'No Change', change

    def save_ndvi_record(self, forest_area_name, ndvi_value):
        try:
            forest_area = ForestArea.objects.get(name=forest_area_name)
        except ForestArea.DoesNotExist:
            raise ValueError(f"Forest area '{forest_area_name}' does not exist.")
        
        ndvi_record = NDVIRecord(forest_area=forest_area, ndvi_values=ndvi_value)
        ndvi_record.save()
        return ndvi_record