#
#
# Kindesunterhaltsrechner gemaess Duesseldorfer Tabelle fuer privat
# krankenversicherte Unterhaltspflichtige
#
# 28.07.2023, Moritz Deger, https://github.com/mdeger



import numpy as np
from datetime import date


# aktuelle Duesseldorfer Tabelle (Stand 2023)
DusTabV          = 2023
# Angaben aus der Tabelle
DusTabAlterMin   = np.array( [0, 6, 12, 18] )
DusTabLabels     = np.array( \
    [ "Stufe",  "BerNettoMax",  "0-5",  "6-11", "12-17",    "ab 18",    "%" ])
DusTabZahlBetrag = np.array([\
    [       1,           1900,   312,    377,    463,      378,   100],
    [       2,           2300,   334,    403,    493,      410,   105],
    [       3,           2700,   356,    428,    522,      441,   110],
    [       4,           3100,   378,    453,    552,      473,   115],
    [       5,           3500,   400,    478,    581,      504,   120],
    [       6,           3900,   435,    518,    628,      554,   128],
    ])
DusTabNotwdgSelbstBehalt            = 1370
DusTabNotwdgSelbstBehaltWohnKosten  =  520



class KindesUnterhalt:

    def __init__(self):
        '''Kindesunterhaltsrechner fuer privat krankenversicherte 
        Unterhaltspflichtige
        Anwendungsablauf:
        0. Klasse instantiieren mittels __init__() (automatisch bei Aufruf)
        1. Parameter der Instanz setzen (Brutto, AbzuegeNetto, AbzuegeBerNetto, 
           Wohnkosten, KinderGeburtstage, ggf. Stichtag)
        2. Auswerten mittels get_KindesUnterhalt()
        3. Ergebnis darstellen mittels print_Result()
        '''
        self.AbzuegeNetto = {
            "PrivKVPV"  :  300.,
            "PKVKind"   :   20.,
            "Einkommensteuer" : 400.,
            "Kirchensteuer" : 40.
            }
        self.AbzuegeBerNetto = {
            "RisikoLebensVersicherung" : 10.,
            }
        self.Brutto            = 3000.
        self.Wohnkosten        = DusTabNotwdgSelbstBehaltWohnKosten
        self.AltersvorsorgeQuote = 0.04
        self.KinderGeburtstage = np.array([\
            np.datetime64('2011-11-11'), \
            np.datetime64('2012-12-12')])
        self.Stichtag          = np.datetime64( date.today() )
        self.KinderSummenEndIndex = len(self.KinderGeburtstage)
    
    
    def get_BerBedAufwdg(self, Netto):
        """Berechnung der zulaessigen berufsbedingten Aufwaendungen"""
        self.BerBedAufwdg = min( np.round( 0.05*Netto, 2), 150. )
    
    
    def get_Netto(self):
        """Berechnung des Nettoeinkommens aus dem Bruttoeinkommen"""
        self.Netto = self.Brutto
        for key in self.AbzuegeNetto.keys():
            self.Netto -= self.AbzuegeNetto[key]
        self.get_BerBedAufwdg( self.Netto )
    
    
    def get_BerNetto(self, Mangelfall=True):
        """Berechnung des bereinigten Nettoeinkommens nach weiteren Abzuegen"""
        self.BerNetto = self.Netto - self.BerBedAufwdg
        if Mangelfall:
            # Vorauswertung fuer etwaigen Mangelfall
            self.SelbstBehalt = DusTabNotwdgSelbstBehalt \
                + self.Wohnkosten - DusTabNotwdgSelbstBehaltWohnKosten
            self.VerteilungsMasse = self.BerNetto - self.SelbstBehalt
        else:
            self.AbzuegeBerNetto['Altersvorsorge'] = \
                self.AltersvorsorgeQuote * self.Brutto
            for key in self.AbzuegeBerNetto.keys():
                self.BerNetto -= self.AbzuegeBerNetto[key]
    
    
    def get_UnterhaltsStufenMod(self):
        """berechnet den gaengigen Unterhaltsstufenmodifikator bei ueber 2 
        Kindern"""
        self.UnterhaltsStufenMod = max( [len(self.KinderGeburtstage) - 2, 0] )
    
    
    def get_UnterhaltsStufe(self):
        self.StufeIdx = np.searchsorted( DusTabZahlBetrag[:,1], self.BerNetto )\
            - self.UnterhaltsStufenMod
        self.Stufe = DusTabZahlBetrag[ self.StufeIdx,0 ]
    
    
    def get_KindesUnterhalt_idx( self, idx, MinU=False ):
        """liest den Kindesunterhalt aus der Tabelle aus"""
        AlterD = self.Stichtag - self.KinderGeburtstage[idx]
        AlterY = AlterD.astype(int) / 365
        AlterIdx = DusTabAlterMin.searchsorted( AlterY + 0.1 ) - 1
        if MinU:
            StufeIdx = 0
        else:
            StufeIdx = self.StufeIdx
        return DusTabZahlBetrag[ StufeIdx, AlterIdx + 2 ] # Offset of 2!
    
    
    def get_KindesUnterhalt(self):
        """Berechnung des Kindesunterhalts"""
        self.get_Netto()
        self.get_BerNetto()

        # Mangelfallpruefung
        self.ZahlBetragMinU = \
            np.array([ self.get_KindesUnterhalt_idx( i, MinU=True ) \
            for i in range( len( self.KinderGeburtstage) ) ])
        self.ZahlBetragMinUGesamt = np.sum( self.ZahlBetragMinU )
        self.Deckungsfaktor = \
            min ( self.VerteilungsMasse / self.ZahlBetragMinUGesamt, 1.)
        self.IstMangelFall  = self.Deckungsfaktor < 1
        
        # Berechnung des Zahlbetrags
        if self.IstMangelFall:
            self.ZahlBetrag = \
                np.round ( self.ZahlBetragMinU * self.Deckungsfaktor, 2)
        else:
            # Neuberechnung des bereinigten Netto da kein Mangelfall
            self.get_BerNetto( False )
            self.get_UnterhaltsStufenMod()
            self.get_UnterhaltsStufe()
            self.ZahlBetrag = np.array([ self.get_KindesUnterhalt_idx( i ) \
                for i in range( len( self.KinderGeburtstage) ) ])
        
        self.ZahlBetragGesamt = np.sum( self.ZahlBetrag )
    
    
    def print_Result(self):
        """Ausgabe der Berechnungsergebnisse"""
        print('\n' +'Kindesunterhaltsberechnung nach Duesseldorfer Tabelle '+str(DusTabV)+'\nzum Stichtag '+self.Stichtag.astype(str)+':\n==========================================================')
        print('\n' +'--- Einkommensberechnung ---')
        print('Bruttoeinkommen: ' + str(self.Brutto))
        for key in self.AbzuegeNetto:
            print('./ ab '+ key + ': '+ "{:.2f}".format( self.AbzuegeNetto[key]))
        print('Nettoeinkommen: '+ "{:.2f}".format( self.Netto))
        print('./ ab berufsbedingte Aufwendungen '+"{:.2f}".format(self.BerBedAufwdg))
        if not self.IstMangelFall:
            for key in self.AbzuegeBerNetto:
                print('./ ab '+ key + ': '+ "{:.2f}".format( self.AbzuegeBerNetto[key]))
        print('Bereinigtes Nettoeinkommen: '+ "{:.2f}".format( self.BerNetto))
        print('\n' + '--- Unterhaltsberechnung ---')
        if self.IstMangelFall:
            print('Mangelfall mit Deckungsfaktor ' + "{:.2f}".format( np.round(self.Deckungsfaktor, 2)))
            print('Notwendiger Eigenbedarf nach Tabelle: ' +"{:.2f}".format(DusTabNotwdgSelbstBehalt))
            print('Wohnkosten (Warmmiete): '+"{:.2f}".format(self.Wohnkosten))
            print('davon beruecksichtigt in notw. Eigenbedarf: '+"{:.2f}".format(DusTabNotwdgSelbstBehaltWohnKosten))
            print('ergibt Notwendiger Eigenbedarf mit tats. Wohnk.: '+"{:.2f}".format(self.SelbstBehalt))
            print('\n'+'Verteilungsmasse: '+ "{:.2f}".format( self.VerteilungsMasse ))
            print('\n'+'Kind:         Einsatzbetrag:      Unterhalt:')
        else:
            print('Unterhaltsstufe '+str(self.Stufe))
            print('\n'+'Kind:         Mindestbetrag:      Unterhalt:')

        # Ausgabe der Unterhalszahlbetraege
        for i in range(len(self.KinderGeburtstage)):
            print( self.KinderGeburtstage[i].astype(str) + '       ' \
                + "{:.2f}".format(self.ZahlBetragMinU[i]) + '             ' \
                + "{:.2f}".format( self.ZahlBetrag[i] ))
        
        print ('\n' + '(Teil-)Summe' + '    ' \
                + "{:.2f}".format(self.ZahlBetragMinU[:self.KinderSummenEndIndex].sum()) + '             ' \
                + "{:.2f}".format( self.ZahlBetrag[:self.KinderSummenEndIndex].sum() ))
        
        
