function normalize( val, minIn, maxIn, minOut, maxOut )  {
  var r = Math.max( Math.min( val, maxIn ), minIn) ;
  var deltaIn = maxIn - minIn;
  var deltaOut = maxOut - minOut;
  r = minOut + deltaOut * (r - minIn) / deltaIn;
  r = Math.floor(r);
  return r;
}

function createmap() {
  var map = new ol.Map({
    target: 'map',
    layers: [
      new ol.layer.Tile({
        source: new ol.source.Stamen({
           layer: 'toner'
        })
      })
    ],
    view: new ol.View({
      center: ol.proj.fromLonLat([5.335, 60.394]),
      zoom: 11
    })
  });
  var styleFunc = function(list, timestamp) {
    return function(feature, resolution) {
      var data = feature.getProperties()["sensor"][list];
      if (data.length == 0 || data[data.length - 1] == undefined)
        return new ol.style.Style({visible: false});

      var val = data[data.length - 1].value;
      var norm_val = normalize(val,0,35,0,255);
      var color = 'rgba(' + norm_val + ',' + (255 - norm_val) + ',0,1)';
      return new ol.style.Style({
        fill: new ol.style.Fill({color: color})
      });
    };
  };
  var vectorSource = new ol.source.Vector();
  var positions = [];
  values.forEach(function(value) {
    var coordinate = ol.proj.transform([value.long, value.lat], 'EPSG:4326', 'EPSG:3857');
    vectorSource.addFeature(
      new ol.Feature({
        "geometry" : new ol.geom.Circle(coordinate,
          100),
        "sensor": value }));
    positions.push({
       coords: [value.long, value.lat],
       value: value.last,
       name: value.locname
    });
  });

  // Create Voronoi layer
  var voronoi = d3.geom.voronoi()
    .x(function(d) { return d.coords[0]; })
    .y(function(d) { return d.coords[1]; })
    .clipExtent([[-180, -85], [180, 85]]);

  var polygons = voronoi(positions);
  console.log(polygons);
		
  var featuresPoly = new ol.source.Vector({});

  var i = 0;
  polygons.forEach(function(polygon) { 
    try {
      var feature = new ol.Feature({
        geometry: new ol.geom.Polygon([polygon]),
        index: i
      });

      feature.getGeometry().transform('EPSG:4326', 'EPSG:3857');
      featuresPoly.addFeature(feature);
    } catch (err) {
      console.log("feature error:" + err + " " + i);
    }
    i++;
  });

  var polyStyleFunc = function (polygon) {
      var index = polygon.get("index");
      var red_val = normalize(positions[index].value,0,25,0,255);
      var green_val = normalize(positions[index].value,25,35,255,0);
      var gradient = [red_val, green_val, 0, 0.4];
  return [
      new ol.style.Style({
        fill: new ol.style.Fill({ color: gradient, weight: 1 }),
        stroke: new ol.style.Stroke({ color: gradient, width: 1 })
      })
    ];
  };

  var vectorLayer = new ol.layer.Vector({
    source: featuresPoly,
    style: polyStyleFunc
  });
  // End Voronoi code

  return {
    onSelect: function(callback) {
      selectClick.on('select', function(e) {
        e.selected.forEach(function(feature) {
          callback(feature.getProperties()["sensor"]["id"]);
        });
      });
    },
    showDataFor: function(sensors, key, timestamp) {
       map.getLayers().forEach(function(l) {
         if (l.get("name") === "layer") map.removeLayer(l);
      });
      var layer = new ol.layer.Vector({
        source: vectorSource,
        style: styleFunc(key, timestamp)
      });
      layer.set("name", "layer");
      map.addLayer(layer);
      map.addLayer(vectorLayer);
    }
  };
};
