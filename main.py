from kivy.app import App
from kivy.garden.mapview import MapView, MapMarker
from kivy.uix.boxlayout import BoxLayout
from kivy.utils import platform
from time import sleep
from plyer import gps
import json, requests

class Principal(BoxLayout):
    meu_local = (-22.9035, -43.2096)
    mapa = MapView(zoom=15, lat=meu_local[0], lon=meu_local[1])
    marcson = MapMarker(lat=meu_local[0], lon=meu_local[1])

    def on_location(self, **kwargs):
        self.meu_local = (kwargs['lat'], kwargs['lon'])


        self.mapa.center_on(self.meu_local[0], self.meu_local[1])
        self.marcson.lat = self.meu_local[0]
        self.marcson.lon = self.meu_local[1]

        self.mapa.add_marker(self.marcson)

    def start(self, tempo, distancia):
        gps.start(tempo, distancia)

    def marcar_onibus(self):
        from geopy.distance import vincenty
        url = 'http://dadosabertos.rio.rj.gov.br/apiTransporte/apresentacao/rest/index.cfm/obterTodasPosicoes'
        resposta = requests.get(url)
        dados = json.loads(resposta.text)

        for i in range(len(dados['DATA'])):
            distancia =vincenty(self.meu_local, (dados['DATA'][i][3], dados['DATA'][i][4])).meters
            if distancia < 2000:
                self.mapa.add_marker(MapMarker(lat=dados['DATA'][i][3], lon=dados['DATA'][i][4], source='bolinha.png'))


    def __init__(self, **kwargs):
        super(Principal, self).__init__(**kwargs)
        self.add_widget(self.mapa)
        if platform == 'android':
            try:
                gps.configure(on_location=self.on_location)
            except NotImplementedError:
                pass
            self.start(1000, 0)

        sleep(1.)
        self.marcar_onibus()


class Aplicativo(App):
    def build(self):
        return Principal()

if __name__ == '__main__':
    Aplicativo().run()
