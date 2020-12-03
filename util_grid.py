# -*- coding: utf-8 -*-
"""
Created on Mon Nov 30 08:26:50 2020

@author: U546416
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import pandapower as pp
import pandapower.control as ppc

def yearly_profile(df, step=30, day_ini=0, nweeks=None, ndays=None):
    """
    """
    if not (nweeks is None):
        step = 60 / (df.shape[0]/(7 * nweeks * 24))
    elif not (ndays is None):
        step = 60 / (df.shape[0]/(ndays * 24))
    mult = int(np.ceil(375/(df.shape[0]/(24*60/step))))
    
    idi = day_ini * 24 * int(60/step)
    ide = idi + 365 * 24 * int(60/step)
    cols = df.columns
    
    return pd.DataFrame(np.tile(df.values, (mult,1)), columns=cols).iloc[idi:ide,:]
  
def add_extra(net_el, idxs, vals, param_net='Feeder'):
    if not (param_net in net_el):
        net_el[param_net] = None
    net_el[param_net][idxs] = vals
    
def add_tech_types(net, tech):
    """ Add std_type to an existing net
    """
    for i, t in tech.iterrows():
        # i is ID of tech, t is tech data
        data = dict(c_nf_per_km=t.C,
                    r_ohm_per_km=t.R,
                    x_ohm_per_km=t.X,
                    max_i_ka=t.Imax/1000,
                    q_mm=t.Section,
                    type='oh' if t.Type == 'Overhead' else 'cs')
        pp.create_std_type(net, name=i, data=data, element='line')      
            
def create_pp_grid(nodes, lines, tech, loads, n0, 
                   hv=True, ntrafos_hv=2, vn_kv=20,
                   tanphi=0.3, hv_trafo_controller=True, verbose=True):
    """
    """
    if verbose:
        print('Starting!')
    # 0- empty grid
    net = pp.create_empty_network()
    # 1- std_types
    if verbose:
        print('\tTech types')
    add_tech_types(net, tech)
    # 2 - Create buses
    if verbose:
        print('\tBuses')
    idxs = pp.create_buses(net, len(nodes), vn_kv=vn_kv, name=nodes.index, 
                           geodata=nodes.xyGPS.values, type='b', zone=nodes.Geo.values)
    if 'Feeder' in nodes:
        add_extra(net.bus, idxs, nodes.Feeder.values, 'Feeder')
    # 3- Create lines
    if verbose:
        print('\tLines')
    for linetype in lines.Conductor.unique():
        ls = lines[lines.Conductor == linetype]
        nis = pp.get_element_indices(net, "bus", ls.node_i)
        nes = pp.get_element_indices(net, "bus", ls.node_e)
        idxs = pp.create_lines(net, nis, nes, ls.Length.values/1000, 
                               std_type=linetype, 
                               name=ls.index, geodata=ls.ShapeGPS,
                               df=1., parallel=1, in_service=True)
        if 'Feeder' in lines:
            add_extra(net.line, idxs, ls.Feeder.values, 'Feeder')
    # 4- Create loads
    if verbose:
        print('\tLoads')
    nls = pp.get_element_indices(net, 'bus', loads.node)
    idxs = pp.create_loads(net, nls, name=loads.index, p_mw=loads.Pmax_MW.values, 
                    q_mvar=loads.Pmax_MW.values*tanphi)
    if 'type_load' in loads:
        add_extra(net.load, idxs, loads.type_load.values, 'type_load')
    else:
        add_extra(net.load, idxs, 'Base', 'type_load')
    if 'Geo' in loads:
        add_extra(net.load, idxs, loads.Geo, 'zone')
        
    # Adding external grid
    if verbose:
        print('\tExt Grid')
    if hv:
        # If HV, then add extra bus for HV and add trafo
        b0 = pp.create_bus(net, vn_kv=110, geodata=nodes.xyGPS[n0], name='HV_SS')
        # Adding HV-MV trafo (n x 40MW trafos)
        t = pp.create_transformer(net, hv_bus=b0, lv_bus=n0, 
                                  std_type='40 MVA 110/20 kV', 
                                  name='TrafoSS', parallel=ntrafos_hv) 
        if hv_trafo_controller:
            # Add tap changer controller at MV side of SS trafo
            ppc.DiscreteTapControl(net, t, 0.99, 1.01, side='lv')
    else:
        b0 = n0
    pp.create_ext_grid(net, bus=b0)
    
    if verbose:
        print('Finished!')
    return net
