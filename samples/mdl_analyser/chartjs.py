import json
import random

class ChartJS:
    
    def __init__(self, title, chart_type="line", stacked=False):
        self.chart_data_sets = []
        self.stacked = stacked
        self.type = chart_type
        self.data = {}
        self.options = { "title": { "display": True, "text": title }, 'scales': { 'yAxes': [ { 'stacked': stacked } ]}}
        
    def add_data (self, dataset_label, x_val, y_val):
        for chart_data_set in self.chart_data_sets:
            if chart_data_set.label == dataset_label:
                chart_data_set.append(ChartDatalet(x_val, y_val))
                return
        self.chart_data_sets.append(ChartDataset(dataset_label,ChartDatalet(x_val, y_val)))

    def add_option(self, key, value):
        self.chart_options[key] = value

    def add_legends (self, x_label, y_label):
        self.options['scales'] = { 
            'xAxes': [{
                'display': True,
                'scaleLabel': {
                    'display': True,
                    'labelString': x_label
                }
            }],
            'yAxes': [{
                'display': True,
                'stacked': self.stacked,
                'scaleLabel': {
                    'display': True,
                    'labelString': y_label
                }
            }]
        }

    def set_color (self, dataset_label, borderColor, backgroundColor="", fill=True):
        for chart_data_set in self.chart_data_sets:
            if chart_data_set.label == dataset_label:
                chart_data_set.backgroundColor = backgroundColor
                chart_data_set.borderColor = borderColor
                chart_data_set.fill = fill

    def set_legend(self, fontcolor='#000000', position="right", align="center", onClick=""):
        self.options['legend'] = {
            'display': True,
            'position': position,
            'align': align,
            # 'onClick': onClick,
            'labels':{
                'fontColor': fontcolor
            }
        }

    def render_json_config(self):
        output = {}
        output['type'] =  self.type

        sorted_dataset = sorted(
            [ (datalet.data['x'], datalet.data['y'])
            for dataset in self.chart_data_sets
            for datalet in dataset ],
            key=lambda x: x[0]
        )

        uniq_sorted_labels = []

        for x in enumerate(sorted_dataset):
            if sorted_dataset[x[0]][0] != sorted_dataset[x[0]-1][0]:
                uniq_sorted_labels.append(str(x[1][0]))

        output['data'] = { 
            'labels': uniq_sorted_labels,
            'datasets': [ dataset.dump_json() for dataset in self.chart_data_sets ]
            }
        
        output['options'] = self.options

        return json.dumps(output)

def _random_rgb():
    return "rgb({},{},{})".format(random.randrange(0,255,1),random.randrange(0,255,1),random.randrange(0,255,1))



class ChartDatalet:
    def __init__(self, x_value, y_value):
        self.data = {}
        self.data['x'] = x_value
        self.data['y'] = y_value

    def __str__(self):
        return str(self.data)
    
    def get_data(self):
        return self.data['y']

    def get_labels(self):
        return self.data['x']

class ChartDataset:
    def __init__(self, dataset_label, datalet):
        self.dataset = [datalet]
        self.label = dataset_label
        self.backgroundColor = _random_rgb()
        self.borderColor = self.backgroundColor 
        self.miscoptions = {}
        self.fill = False
    
    def __iter__(self):
        return self.ChartDatasetInterator(self)

    def __len__(self):
        return len(self.dataset)

    def append(self, Chartlet):
        if isinstance(Chartlet, ChartDatalet):
            self.dataset.append(Chartlet)
        else:
            raise TypeError("'ChartDatalet' is expected")

    def label(self, label):
        self.label = label

    def misc(self, key, value):
        self.miscoptions[key] = value

    def dump_json(self):
        output = { 'label': self.label, 'backgroundColor': self.backgroundColor, "borderColor": self.borderColor, "fill": self.fill }
        output['data'] = [ char_datalet.get_data() for char_datalet in self ]

        return ({ **output, **self.miscoptions})

    class ChartDatasetInterator:
        def __init__(self, DataSetObj):
            self.ChartDatasetObj = DataSetObj
            self._index = 0

        def __iter__(self):
            return self

        def __next__(self):
            if self._index < len(self.ChartDatasetObj):
                return_value = self.ChartDatasetObj.dataset[self._index]
                self._index += 1
                return return_value
            else:
                raise StopIteration
