from flavio.physics.bdecays.common import lambda_K
from math import sqrt, pi
from flavio.physics.bdecays.wilsoncoefficients import wctot_dict
from flavio.physics.running import running
from flavio.physics.bdecays.formfactors import FormFactorParametrization as FF
from flavio.config import config
from flavio.physics.bdecays.common import lambda_K, beta_l, meson_quark, meson_ff
from flavio.physics.bdecays import matrixelements, angular
from flavio.physics import ckm

def get_wceff(q2, wc_obj, par, B, V, lep):
    scale = config['bdecays']['scale_bvll']
    wc = wctot_dict(wc_obj, meson_quark[(B,V)]+lep+lep, scale, par)
    xi_u = ckm.xi('u',meson_quark[(B,V)])(par)
    xi_t = ckm.xi('t',meson_quark[(B,V)])(par)
    qiqj=meson_quark[(B,V)]
    Yq2 = matrixelements.Y(q2, wc, par, scale, qiqj) + (xi_u/xi_t)*matrixelements.Yu(q2, wc, par, scale, qiqj)
        #   b) NNLO Q1,2
    delta_C7 = matrixelements.delta_C7(par=par, wc=wc, q2=q2, scale=scale, qiqj=qiqj)
    delta_C9 = matrixelements.delta_C9(par=par, wc=wc, q2=q2, scale=scale, qiqj=qiqj)
    mb = running.get_mb(par, scale)
    ll = lep + lep
    c = {}
    c['7']  = wc['C7eff_'+qiqj]      + delta_C7
    c['7p'] = wc['C7effp_'+qiqj]
    c['v']  = wc['C9_'+qiqj+ll]      + delta_C9 + Yq2
    c['vp'] = wc['C9p_'+qiqj+ll]
    c['a']  = wc['C10_'+qiqj+ll]
    c['ap'] = wc['C10p_'+qiqj+ll]
    c['s']  = 1/2 * mb * wc['CS_'+qiqj+ll]
    c['sp'] = 1/2 * mb * wc['CSp_'+qiqj+ll]
    c['p']  = 1/2 * mb * wc['CP_'+qiqj+ll]
    c['pp'] = 1/2 * mb * wc['CPp_'+qiqj+ll]
    c['t']  = 0
    c['tp'] = 0
    return c

def get_ff(q2, par, B, V):
    return FF.parametrizations['bsz3'].get_ff(meson_ff[(B,V)], q2, par)

def prefactor_new(q2, par, B, V, lep):
    GF = par['Gmu']
    scale = config['bdecays']['scale_bvll']
    alphaem = running.get_alpha(par, scale)['alpha_e']
    ml = par[('mass',lep)]
    mB = par[('mass',B)]
    mV = par[('mass',V)]
    tauB = par[('lifetime',B)]
    laB= lambda_K(mB**2, mV**2, q2)
    laGa = lambda_K(q2, ml**2, ml**2)
    di_dj = meson_quark[(B,V)]
    xi_t = ckm.xi('t',di_dj)(par)
    if q2 <= 4*ml**2:
        return 0
    return ( sqrt(
    sqrt(laB)*sqrt(laGa)/(2**9 * pi**3 * mB**3 * q2)
    ) * 4*GF/sqrt(2)*xi_t*alphaem/(4*pi) )

def get_angularcoeff(q2, wc_obj, par, B, V, lep):
    scale = config['bdecays']['scale_bvll']
    wc = get_wceff(q2, wc_obj, par, B, V, lep)
    ml = par[('mass',lep)]
    mB = par[('mass',B)]
    mV = par[('mass',V)]
    mb = running.get_mb(par, scale)
    N = prefactor_new(q2, par, B, V, lep)
    ff = get_ff(q2, par, B, V)
    h = angular.helicity_amps(q2, mB, mV, mb, 0, ml, ml, ff, wc, N)
    J = angular.angularcoeffs_general(h, q2, mB, mV, mb, 0, ml, ml)
    return J
