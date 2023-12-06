# -*- encoding: utf-8 -*-
"""
 * Project Name: main.py
 * Created by migueldcga
 * Date: 02/11/2023
 * Time: 23:53
 *
 * Edited by: 
 * Date: 
 * Time: 
"""
# Não remover a linha de importação abaixo
import copy
import re
from typing import Any

import geopandas as gpd
from tqdm import tqdm

from bdgd_tools.model.Converter import convert_ttranf_phases, convert_tfascon_bus, convert_tten, convert_ttranf_windings, convert_tfascon_conn, convert_tpotaprt, convert_tfascon_phases,  convert_tfascon_bus_prim,  convert_tfascon_bus_sec,  convert_tfascon_bus_terc, convert_tfascon_phases_trafo
from bdgd_tools.core.Utils import create_output_file

from dataclasses import dataclass


@dataclass
class Transformer:

    _feeder: str = ""

    _bus1: str = ""
    _bus2: str = ""
    _bus3: str = ""
    _suffix_bus1: str = ""
    _suffix_bus2: str = ""
    _suffix_bus3: str = ""
    _transformer: str = ""
    _ten_lin_se: str = ""
    _lig_fas_p: str = ""
    _lig_fas_s: str = ""
    _lig_fas_t: str = ""

    v_pri: float = 0
    v_sec: float = 0

    _tap: float = 0.0
    _MRT: int = 0
    _tip_trafo: str = ""
    
    _phases: int = 0                            
    _bus1_nodes: str = ""
    _bus2_nodes: str = ""
    _bus3_nodes: str = ""
    _windings: str =  ""
    _conn_p: str = ""
    _conn_s: str = ""
    _conn_t: str = ""
    _kvas: int = 0
    _loadloss: float = 0.0
    _noloadloss: float = 0.0
    _kvs: str = ""
    
    @property
    def feeder(self):
        return self._feeder

    @feeder.setter
    def feeder(self, value):
        self._feeder = value

    @property
    def bus1(self):
        return self._bus1

    @bus1.setter
    def bus1(self, value):
        self._bus1 = value

    @property
    def bus2(self):
        return self._bus2

    @bus2.setter
    def bus2(self, value):
        self._bus2 = value

    @property
    def bus3(self):
        return self._bus3

    @bus3.setter
    def bus3(self, value):
        self._bus3 = value

    @property
    def transformer(self):
        return self._transformer

    @transformer.setter
    def transformer(self, value):
        self._transformer = value

    @property
    def ten_lin_se(self):
        return self._ten_lin_se

    @ten_lin_se.setter
    def ten_lin_se(self, value):
        self._ten_lin_se = value

    @property
    def kvas(self):
        return self._kvas

    @kvas.setter
    def kvas(self, value):
        self._kvas = value

    @property
    def tap(self):
        return self._tap

    @tap.setter
    def tap(self, value):
        self._tap = value

    @property
    def MRT(self):
        return self._MRT

    @MRT.setter
    def MRT(self, value):
        self._MRT = value

    @property
    def tip_trafo(self):
        return self._tip_trafo

    @tip_trafo.setter
    def tip_trafo(self, value):
        self._tip_trafo = value

    @property
    def phases(self):
        return self._phases

    @phases.setter
    def phases(self, value):
        self._phases = value

    @property
    def bus1_nodes(self):
        return self._bus1_nodes

    @bus1_nodes.setter
    def bus1_nodes(self, value):
        self._bus1_nodes = value

    @property
    def bus2_nodes(self):
        return self._bus2_nodes

    @bus2_nodes.setter
    def bus2_nodes(self, value):
        self._bus2_nodes = value

    @property
    def bus3_nodes(self):
        return self._bus3_nodes

    @bus3_nodes.setter
    def bus3_nodes(self, value):
        self._bus3_nodes = value

    @property
    def lig_fas_p(self):
        return self._lig_fas_p

    @lig_fas_p.setter
    def lig_fas_p(self, value):
        self._lig_fas_p = value

    @property
    def lig_fas_s(self):
        return self._lig_fas_s

    @lig_fas_s.setter
    def lig_fas_s(self, value):
        self._lig_fas_s = value

    @property
    def lig_fas_t(self):
        return self._lig_fas_t

    @lig_fas_t.setter
    def lig_fas_t(self, value):
        self._lig_fas_t = value
        
    @property
    def v_pri(self):
        return self._v_pri

    @v_pri.setter
    def v_pri(self, value):
        self._v_pri = value

    @property
    def v_sec(self):
        return self._v_sec

    @v_sec.setter
    def v_sec(self, value):
        self._v_sec = value
        

    @property
    def windings(self):
        return self._windings

    @windings.setter
    def windings(self, value):
        self._windings = value

    @property
    def conn_p(self):
        return self._conn_p

    @conn_p.setter
    def conn_p(self, value):
        self._conn_p = value

    @property
    def conn_s(self):
        return self._conn_s

    @conn_s.setter
    def conn_s(self, value):
        self._conn_s = value

    @property
    def conn_t(self):
        return self._conn_t

    @conn_t.setter
    def conn_t(self, value):
        self._conn_t = value

    @property
    def loadloss(self):
        return self._loadloss

    @loadloss.setter
    def loadloss(self, value):
        self._loadloss = value

    @property
    def noloadloss(self):
        return self._noloadloss

    @noloadloss.setter
    def noloadloss(self, value):
        self._noloadloss = value


    def kvs(self):
        kVs: str = ""
        if self.tip_trafo == 'MT':
            kVs = f"{self.v_pri} {self.v_sec}"
    
        elif self.lig_fas_t in ["BN", "CN", "AN"] or self.lig_fas_s == "ABN":
            kVs = (
                f"{self.voltage_enroll(self.lig_fas_p, self.v_pri)} " +
                f"{self.v_sec / 2} {self.v_sec / 2}")
    
        elif self.lig_fas_t == "XX" and self.lig_fas_s in ["AN", "BN", "CN", "AB", "BC", "CA", "AC", "ABC"]:
            kVs = (
                f"{self.voltage_enroll(self.lig_fas_p, self.v_pri)} " +
                f"{self.voltage_enroll_sec(self.lig_fas_s, self.v_sec)}"
        )
    
        elif self.lig_fas_t == "0" and self.lig_fas_s == "ABCN":
            print(self.lig_fas_p,self.v_pri)
            kVs = (
                self.voltage_enroll(self.lig_fas_p, self.v_pri) + 
                f"{self.v_sec}")

        return kVs
        
    
    def voltage_enroll(self, cod_phase, voltage_kv):
        
        if cod_phase in ["A", "B", "C", "AN", "BN", "CN", "ABN", "BCN", "CAN", "ABCN"]:
            return voltage_kv / (3 ** 0.5)
        elif cod_phase in ["AB", "BC", "CA", "ABC"]:
            return str(voltage_kv)
    
    def voltage_enroll_sec(self, cod_phase, voltage_kv):
        
        if cod_phase in ["A", "B", "C", "AN", "BN", "CN"]:
            return voltage_kv
        elif cod_phase in ["ABN", "BCN", "CAN", "ABCN"]:
            return voltage_kv / 3 ** 0.5
        elif cod_phase in ["AB", "BC", "CA", "ABC"]:
            return str(voltage_kv)
        
    
    def adapting_string_variables(self):

        """
        Format and adapt instance variables to create strings for OpenDSS input.

        This method prepares and formats instance variables to be used as strings in OpenDSS input.
        It constructs strings for voltage levels, bus definitions, kVA ratings, and tap settings based
        on the values stored in the object.

        Returns:
            tuple of strings: A tuple containing the following formatted strings:
                - kvs: A string representing voltage levels in kV for different phases.
                - buses: A string representing bus definitions in OpenDSS format.
                - kvas: A string representing kVA ratings 
                - taps: A string representing tap settings 



            Calling this method will format the variables and return a tuple of strings for OpenDSS input.

        """

        if self.MRT == 1:
            if self.bus3 != "0":
                buses = f'"MRT_{self.bus1}TRF_{self.transformer}.{self.bus1_nodes}" "{self.bus2}.{self.bus2_nodes}" "{self.bus3}.{self.bus3_nodes}" '
                conns = f'{self.conn_p} {self.conn_s} {self.conn_t}'
            else:
                buses = f'"MRT_{self.bus1}TRF_{self.transformer}.{self.bus1_nodes}" "{self.bus2}.{self.bus2_nodes}" '   
                conns = f'{self.conn_p} {self.conn_s}'
            
            MRT = self.pattern_MRT()
        else:
            if self.bus3 != "0":
                buses = f'"{self.bus1}.{self.bus1_nodes}" "{self.bus2}.{self.bus2_nodes}" "{self.bus3}.{self.bus3_nodes}"'
                conns = f'{self.conn_p} {self.conn_s} {self.conn_t}'
            else:
                buses = f'"{self.bus1}.{self.bus1_nodes}" "{self.bus2}.{self.bus2_nodes}"'   
                conns = f'{self.conn_p} {self.conn_s}'
            MRT = ""


        kvas = ' '.join([f'{self.kvas}' for _ in range(self.windings)])

        taps = ' '.join([f'{self.tap}' for _ in range(self.windings)])


        return self.kvs(), buses, conns, kvas, taps, MRT

    def pattern_reactor(self):
        
        return  f'New "Reactor.TRF_{self.transformer}" phases=1 bus1="{self.bus2}.4" R=15 X=0 basefreq=60'
    
    def pattern_MRT(self):
        
        return (f'New "Linecode.LC_MRT_TRF_{self.transformer}_1" nphases=1 basefreq=60 r1=15000 x1=0 units=km normamps=0\n'
                f'New "Linecode.LC_MRT_TRF_{self.transformer}_2" nphases=2 basefreq=60 r1=15000 x1=0 units=km normamps=0\n'
                f'New "Linecode.LC_MRT_TRF_{self.transformer}_3" nphases=3 basefreq=60 r1=15000 x1=0 units=km normamps=0\n'
                f'New "Linecode.LC_MRT_TRF_{self.transformer}_4" nphases=4 basefreq=60 r1=15000 x1=0 units=km normamps=0\n'
                f'New "Line.Resist_MTR_TRF_{self.transformer}" phases=1 bus1="{self.bus1}.{self.bus1_nodes}" bus2="MRT_{self.bus1}TRF_{self.transformer}.{self.bus1_nodes}" linecode="LC_MRT_TRF_{self.transformer}_1" length=0.001 units=km\n')

    def full_string(self) -> str:

        self.kvs, self.buses, self.conns, self.kvas, self.taps, MRT= Transformer.adapting_string_variables(self)

      
        return (f'New \"Transformer.TRF_{self.transformer}" phases={self.phases} '
                f'windings={self.windings} '
                f'buses=[{self.buses}] '
                f'conns=[{self.conns}] '
                f'kvs=[{self.kvs}] '
                f'taps=[{self.taps}] '
                f'kvas=[{self.kvas}] '
                f'%loadloss={self.loadloss:.3f} %noloadloss={self.noloadloss:.3f}\n'
                f'{MRT}'
                f'{self.pattern_reactor()}')

    def __repr__(self):

        self.kvs, self.buses, self.conns, self.kvas, self.taps, MRT= Transformer.adapting_string_variables(self)

      
        return (f'New \"Transformer.TRF_{self.transformer}" phases={self.phases} '
                f'windings={self.windings} '
                f'buses=[{self.buses}] '
                f'conns=[{self.conns}] '
                f'kvs=[{self.kvs}] '
                f'taps=[{self.taps}] '
                f'kvas=[{self.kvas}] '
                f'%loadloss={self.loadloss:.3f} %noloadloss={self.noloadloss:.3f}\n'
                f'{MRT}'
                f'{self.pattern_reactor()}')


    @staticmethod
    def _process_static(transformer_, value):
        """
        Static method to process the static configuration for a transformer object.

        Args:
            transformer_ (object): A transformer object being updated.
            value (dict): A dictionary containing the static configuration.

        This method processes the static configuration by iterating through the
        key-value pairs of the 'value' dictionary and directly setting the
        corresponding attribute on the transformer object with the static value.
        """
        for static_key, static_value in value.items():
            setattr(transformer_, f"_{static_key}", static_value)
            

    @staticmethod
    def _process_direct_mapping(transformer_, value, row):
        """
        Static method to process the direct mapping configuration for a transformer object.

        Args:
            transformer_ (object): A transformer object being updated.
            value (dict): A dictionary containing the direct mapping configuration.
            row (pd.Series): A row from the GeoDataFrame containing transformer-related data.

        This method processes the direct mapping configuration by iterating through the
        key-value pairs of the 'value' dictionary and directly setting the corresponding
        attribute on the transformer object using the value from the row.
        """
        for mapping_key, mapping_value in value.items():
            setattr(transformer_, f"_{mapping_key}", row[mapping_value])

    @staticmethod
    def _process_indirect_mapping(transformer_, value, row):
        """
        Static method to process the indirect mapping configuration for a transformer object.

        Args:
            transformer_ (object): A transformer object being updated.
            value (dict): A dictionary containing the indirect mapping configuration.
            row (pd.Series): A row from the GeoDataFrame containing transformer-related data.

        This method processes the indirect mapping configuration by iterating through the
        key-value pairs of the 'value' dictionary. If the value is a list, it treats the
        first element as a parameter name and the second element as a function name. The
        method then retrieves the parameter value from the row and calls the specified
        function with that parameter value. The result is then set as an attribute on the
        transformer object.

        If the value is not a list, the method directly sets the corresponding attribute on
        the transformer object using the value from the row.
        """
        for mapping_key, mapping_value in value.items():
            if isinstance(mapping_value, list):
                param_name, function_name = mapping_value
                function_ = globals()[function_name]
                param_value = row[param_name]
                setattr(transformer_, f"_{mapping_key}", function_(str(param_value)))        
            else:
                setattr(transformer_, f"_{mapping_key}", row[mapping_value])

    @staticmethod
    def _process_calculated(transformer_, value, row):
        """
        Static method to process the calculated mapping configuration for a transformer object.

        Args:
            transformer_ (object): A transformer object being updated.
            value (dict): A dictionary containing the direct mapping configuration.
            row (pd.Series): A row from the GeoDataFrame containing transformer-related data.

        This method processes the direct mapping configuration by iterating through the
        key-value pairs of the 'value' dictionary and directly setting the corresponding
        attribute on the transformer object using the value from the row.
        """
        for mapping_key, mapping_value in value.items():
            
            expression = ""
            for item in mapping_value:
                if isinstance(item, str) and any(char.isalpha() for char in item):
                    
                    expression = f'{expression} {row[item]}'
                else:
                    expression = f'{expression}{item}'
            param_value = eval(expression)
           
            setattr(transformer_, f"_{mapping_key}", param_value)
            


    @staticmethod
    def _create_transformer_from_row(transformer_config, row):
        transformer_ = Transformer()

        for key, value in transformer_config.items():
            if key == "static":
                transformer_._process_static(transformer_, value)
            elif key == "direct_mapping":
                transformer_._process_direct_mapping(transformer_, value,row)
            elif key == "indirect_mapping":
                transformer_._process_indirect_mapping(transformer_, value,row)
            elif key == "calculated":
                transformer_._process_calculated(transformer_, value, row)

        return transformer_

    @staticmethod
    def create_transformer_from_json(json_data: Any, dataframe: gpd.geodataframe.GeoDataFrame):
        transformers = []
        transformer_config = json_data['elements']['Transformer']['UNTRMT']


        progress_bar = tqdm(dataframe.iterrows(), total=len(dataframe), desc="Transformer", unit=" transformers", ncols=100)
        for _, row in progress_bar:
            transformer_ = Transformer._create_transformer_from_row(transformer_config, row)
            transformers.append(transformer_)
            progress_bar.set_description(f"Processing transformer {_ + 1}")
        
        file_name = create_output_file(transformers, transformer_config["arquivo"], feeder=transformer_.feeder)
        
        return transformers, file_name