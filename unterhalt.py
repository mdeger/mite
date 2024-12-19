#
#
# Kindesunterhaltsrechner gemaess Duesseldorfer Tabelle fuer privat
# krankenversicherte Unterhaltspflichtige
#
# 28.07.2023, Moritz Deger, https://github.com/mdeger



import numpy as np
from datetime import date


# Duesseldorfer Tabelle 2025
DusTabV          = 2025
# Angaben aus der Tabelle
DusTabAlterMin   = np.array( [0, 6, 12, 18] )
DusTabLabels     = np.array( \
    [ "Stufe",  "BerNettoMax",  "0-5",  "6-11", "12-17",    "ab 18",    "%" ])
DusTabZahlBetrag = np.array([\
    [       1,           2100,   357,    429,    524,      443,   100],
    [       2,           2500,   382,    457,    557,      478,   105],
    [       3,           2900,   406,    485,    589,      513,   110],
    [       4,           3300,   430,    513,    622,      547,   115],
    [       5,           3700,   454,    540,    654,      582,   120],
    [       6,           4100,   492,    585,    706,      638,   128],
    [       7,           4500,   531,    629,    758,      693,   136],
    [       8,           4900,   570,    673,    810,      748,   144],
    [       9,           5300,   608,    718,    862,      804,   152],
    [      10,           5700,   647,    762,    914,      859,   160],
    ], dtype=float)

# Aenderung Kindergeld von 250 auf 255 EUR vom 19.12.2024 ab 01.01.2025:
DusTabZahlBetrag[:,2:5] = DusTabZahlBetrag[:,2:5] + ( 250 - 255 ) / 2.
DusTabZahlBetrag[:,5] = DusTabZahlBetrag[:,5] + ( 250 - 255 )

DusTabNotwdgSelbstBehalt            = 1450
DusTabNotwdgSelbstBehaltWohnKosten  =  520
DusTabAngemSelbstBehalt             = 1750
DusTabBedarfsKontrollBetrag         = \
    np.array([ DusTabNotwdgSelbstBehalt, 1750, 1850, 1950, 2050, 2150, 2250,\
    2350, 2450, 2550, 2850, 3250, 3750, 4350, 5050 ])


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
        self.KinderMinUFaktor = \
            np.ones( len(self.KinderGeburtstage), dtype=float)
        self.Stichtag          = np.datetime64( date.today() )
        self.SelbstBehaltReduktionsFaktor = 0.
        self.KinderSummenEndIndex = len(self.KinderGeburtstage)
        self.BedarfsAnpassung = {}
    
    
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
            self.SelbstBehalt = ( DusTabNotwdgSelbstBehalt \
                + self.Wohnkosten - DusTabNotwdgSelbstBehaltWohnKosten ) *\
                (1. - self.SelbstBehaltReduktionsFaktor)
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
        if self.UnterhaltsStufenMod>0:
            print('[I] Stufe wird wegen Anzahl der Kinder um 2 reduziert.')
    
    
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
        ret_ = DusTabZahlBetrag[ StufeIdx, AlterIdx + 2 ] *\
            self.KinderMinUFaktor[idx] # Offset of 2! 
        if idx in self.BedarfsAnpassung.keys():
            #print ( 'Bedarf des Kinds ' + str(idx+1) + ' angepasst: ' + \
            #    str( self.BedarfsAnpassung[idx] ) )
            ret_ += self.BedarfsAnpassung[idx]
        return ret_
    
    
    def get_KindesUnterhalt(self):
        """Berechnung des Kindesunterhalts"""
        self.get_Netto()

        # Mangelfallpruefung
        self.get_BerNetto( True )
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
            fin_ = False
            while not fin_:
                self.ZahlBetrag = np.array([ self.get_KindesUnterhalt_idx( i ) \
                    for i in range( len( self.KinderGeburtstage) ) ])
                # pruefen, ob Bedarfskontrollbetrag unterschritten
                zb_ = self.ZahlBetrag.sum()
                diff_ = self.BerNetto - zb_ - \
                    DusTabBedarfsKontrollBetrag[self.StufeIdx]
                if diff_ < 0:
                    if self.Stufe > 1:
                        print( '[I] Unterhaltssumme in Stufe '+str(self.Stufe)+\
                            ' von '+str(zb_)+\
                            '\n    bei bereinigtem Nettoeinkommen von '+\
                            "{:.2f}".format(self.BerNetto)+\
                            '\n    uebersteigt Bedarfskontrollbetrag von '+\
                            str(DusTabBedarfsKontrollBetrag[self.StufeIdx])+\
                            '\n    um '+"{:.2f}".format(-diff_)+\
                            '. Stufe wird reduziert.' )
                        self.StufeIdx = self.StufeIdx - 1
                        self.Stufe = self.Stufe - 1
                    else:
                        print( 'Unterhaltssumme in Stufe '+str(self.Stufe)+\
                            ' unterschreitet Bedarfskontrollbetrag aber '+\
                            'Stufe 1 ist bereits erreicht. Mangelfall?')
                        fin_ = True
                else:
                    fin_ = True
        self.ZahlBetragGesamt = np.sum( self.ZahlBetrag )
    
    
    def print_Result(self):
        """Ausgabe der Berechnungsergebnisse"""
        print('\n' +'Kindesunterhaltsberechnung nach Duesseldorfer Tabelle '+\
            str(DusTabV)+'\nzum Stichtag '+self.Stichtag.astype(str)+\
            ':\n==========================================================')
        print('\n' +'--- Einkommensberechnung ---')
        print('Bruttoeinkommen: ' + str(self.Brutto))
        for key in self.AbzuegeNetto:
            # zzgl oder abzgl.?
            if self.AbzuegeNetto[key] > 0:
                zzglabzgl = 'abzgl. '
            else:
                zzglabzgl = 'zuzgl. '
            print('./ '+zzglabzgl + key + ': '+ \
                "{:.2f}".format( self.AbzuegeNetto[key]))
        print('Nettoeinkommen: '+ "{:.2f}".format( self.Netto))
        print('./ ab berufsbedingte Aufwendungen '+\
            "{:.2f}".format(self.BerBedAufwdg))
        if not self.IstMangelFall:
            for key in self.AbzuegeBerNetto:
                print('./ ab '+ key + ': '+ \
                    "{:.2f}".format( self.AbzuegeBerNetto[key]))
        print('Bereinigtes Nettoeinkommen: '+ "{:.2f}".format( self.BerNetto))
        print('\n' + '--- Unterhaltsberechnung ---')
        if self.IstMangelFall:
            print('Mangelfall mit Deckungsfaktor ' + \
                "{:.2f}".format( np.round(self.Deckungsfaktor, 2)))
            print('Notwendiger Eigenbedarf nach Tabelle: ' \
                +"{:.2f}".format(DusTabNotwdgSelbstBehalt))
            if self.Wohnkosten != DusTabNotwdgSelbstBehaltWohnKosten:
                print('Wohnkosten (Warmmiete): '+\
                    "{:.2f}".format(self.Wohnkosten))
                print('davon beruecksichtigt in notw. Eigenbedarf: '+"{:.2f}".format(DusTabNotwdgSelbstBehaltWohnKosten))
            if not self.SelbstBehaltReduktionsFaktor==0.:
                print('Selbstbehalt reduziert um Anteil ' + \
                    str(self.SelbstBehaltReduktionsFaktor)+'.')
            print('ergibt Notwendiger Eigenbedarf: '\
                +"{:.2f}".format(self.SelbstBehalt))
            print('\n'+'Verteilungsmasse: '\
                + "{:.2f}".format( self.VerteilungsMasse ))
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
            + "{:.2f}".format(self.ZahlBetragMinU[:self.KinderSummenEndIndex]\
                .sum()) + '             ' \
            + "{:.2f}".format( self.ZahlBetrag[:self.KinderSummenEndIndex]\
                .sum() ))

        self.vbld_Netto    = self.Netto - \
            self.ZahlBetrag[:self.KinderSummenEndIndex].sum()
        self.vbld_BerNetto = self.BerNetto - \
            self.ZahlBetrag[:self.KinderSummenEndIndex].sum()
        self.vbld_BerNetto_UGes = self.BerNetto - self.ZahlBetragGesamt

        print ('\n     Netto abzgl. Unterhalt-Teilsumme:    '+ \
            "{:.2f}".format( self.vbld_Netto ))
        print ('Ber. Netto abzgl. Unterhalt-Teilsumme:    '+ \
            "{:.2f}".format( self.vbld_BerNetto ))
        print ('Ber. Netto abzgl. Gesamt-Unterhalt:       '+ \
            "{:.2f}".format( self.vbld_BerNetto_UGes ))



