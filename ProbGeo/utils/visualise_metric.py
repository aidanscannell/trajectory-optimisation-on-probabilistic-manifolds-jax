import os
import re
import sys

import jax.numpy as np
import matplotlib.pyplot as plt
from jax import vmap

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from derivative_kernel_gpy import DiffRBF
from probabilistic_metric import (calc_G_map, gp_predict)

import datetime
from pathlib import Path
date = datetime.datetime.now()
date_str = str(date.day) + "-" + str(date.month) + "/" + str(date.time()) + "/"
save_name = "/Users/aidanscannell/Developer/python-projects/BMNSVGP/images/visualise_metric/" + date_str
Path(save_name).mkdir(parents=True, exist_ok=True)


def plot_mean_and_var(X, Y_mean, Y_var, llabel='mean', rlabel='variance'):
    fig, axs = plt.subplots(1, 2, figsize=(24, 4))
    plt.subplots_adjust(wspace=0, hspace=0)

    surf_mean = plot_contour(X, Y_mean, ax=axs[0])
    surf_var = plot_contour(X, Y_var, ax=axs[1])
    cbar = fig.colorbar(surf_mean, shrink=0.5, aspect=5, ax=axs[0])
    cbar.set_label(llabel)
    cbar = fig.colorbar(surf_var, shrink=0.5, aspect=5, ax=axs[1])
    cbar.set_label(rlabel)
    return axs


def plot_scatter_matrix(X, jTj, labels=["", "", "", ""]):
    fig, axs = plt.subplots(2, 2, figsize=(24, 8))
    plt.subplots_adjust(wspace=0, hspace=0)

    surf_11 = plot_contour(X, jTj[:, 0, 0], ax=axs[0, 0])
    surf_12 = plot_contour(X, jTj[:, 0, 1], ax=axs[0, 1])
    surf_21 = plot_contour(X, jTj[:, 1, 0], ax=axs[1, 0])
    surf_22 = plot_contour(X, jTj[:, 1, 1], ax=axs[1, 1])
    cbar = fig.colorbar(surf_11, shrink=0.5, aspect=5, ax=axs[0, 0])
    # cbar.set_label('$(E[\mathbf{J}]^T E[\mathbf{J}])_{1,1}$')
    cbar.set_label(labels[0])
    cbar = fig.colorbar(surf_12, shrink=0.5, aspect=5, ax=axs[0, 1])
    # cbar.set_label('$(E[\mathbf{J}]^T E[\mathbf{J}])_{1,2}$')
    cbar.set_label(labels[1])
    cbar = fig.colorbar(surf_21, shrink=0.5, aspect=5, ax=axs[1, 0])
    # cbar.set_label('$(E[\mathbf{J}]^T E[\mathbf{J}])_{2,1}$')
    cbar.set_label(labels[2])
    cbar = fig.colorbar(surf_22, shrink=0.5, aspect=5, ax=axs[1, 1])
    # cbar.set_label('$(E[\mathbf{J}]^T E[\mathbf{J}])_{2,2}$')
    cbar.set_label(labels[3])
    return axs


def plot_contour(X, Y, ax=None):
    if ax is None:
        fig, ax = plt.subplots(1, 1, figsize=(12, 4))
    print('afasdfaa')
    print(X.shape)
    print(Y.shape)
    print((Y.reshape(-1)).shape)
    cont = ax.tricontourf(X[:, 0], X[:, 1], Y.reshape(-1), 15)
    return cont


def create_grid(X, N):
    x1_low, x1_high, x2_low, x2_high = X[:, 0].min(), X[:,
                                                        0].max(), X[:, 1].min(
                                                        ), X[:, 1].max()
    # x1_low, x1_high, x2_low, x2_high = -2., 3., -3., 3.
    sqrtN = int(np.sqrt(N))
    xx = np.linspace(x1_low, x1_high, sqrtN)
    yy = np.linspace(x2_low, x2_high, sqrtN)
    xx, yy = np.meshgrid(xx, yy)
    xy = np.column_stack([xx.reshape(-1), yy.reshape(-1)])
    return xy, xx, yy


def plot_gradient(xy,
                  mu_j,
                  var_j,
                  mu,
                  var,
                  save_name='../../images/visualise_metric/'):
    # axs_j = plot_mean_and_var(xy, mu_j[:, 0, 0], mu_j[:, 1, 0], '$dim_1$',
    #                           '$dim_2$')
    # plt.suptitle("$\mu_j$")
    # plt.savefig(save_name + 'gradient_mean.pdf', transparent=True)

    axs = plot_mean_and_var(xy, mu, var)
    for ax in axs:
        ax.quiver(xy[:, 0], xy[:, 1], mu_j[:, 0, 0], mu_j[:, 1, 0])
    plt.suptitle("$\mathbb{E}[\mathbf{J}] = \mathbf{\mu}_J$")
    plt.savefig(save_name + 'gradient_mean_quiver.pdf', transparent=True)

    # print(mu_j.shape)
    # mu_jT = np.transpose(mu_j, (0, 2, 1))
    # print(mu_jT.shape)
    # jTj = np.matmul(mu_jT, mu_j)  # [1 x 1]
    # print(jTj.shape)
    # fig, axs = plt.subplots(1, 1, figsize=(12, 4))
    # plt.subplots_adjust(wspace=0, hspace=0)
    # surf_jTj = plot_contour(xy, jTj, axs)
    # cbar = fig.colorbar(surf_jTj, shrink=0.5, aspect=5, ax=axs)
    # plt.suptitle("$E[\mathbf{J}] E[\mathbf{J}]^T$")
    # plt.savefig(save_name + 'mu_j_inner_product.pdf', transparent=True)

    mu_jT = np.transpose(mu_j, (0, 2, 1))
    jTj = np.matmul(mu_j, mu_jT)  # [input_dim x input_dim]
    # labels = [
    #     '$(E[\mathbf{J}]^T E[\mathbf{J}])_{1,1}$',
    #     '$(E[\mathbf{J}]^T E[\mathbf{J}])_{1,2}$',
    #     '$(E[\mathbf{J}]^T E[\mathbf{J}])_{2,1}$',
    #     '$(E[\mathbf{J}]^T E[\mathbf{J}])_{2,2}$'
    # ]
    # axs = plot_scatter_matrix(xy, jTj, labels)
    # plt.suptitle("$E[\mathbf{J}]^T E[\mathbf{J}]$")
    # plt.savefig(save_name + 'mu_j_outer_product.pdf', transparent=True)

    traceJTJ = np.trace(jTj, axis1=1, axis2=2)
    fig, axs = plt.subplots(1, 1, figsize=(12, 4))
    plt.subplots_adjust(wspace=0, hspace=0)
    surf_traceJTJ = plot_contour(xy, traceJTJ, axs)
    cbar = fig.colorbar(surf_traceJTJ, shrink=0.5, aspect=5, ax=axs)
    plt.title('$Tr(\mathbb{E}[\mathbf{J}]^T \mathbb{E}[\mathbf{J}])$')
    plt.savefig(save_name + 'trace_mu_j_outer.pdf', transparent=True)

    axs_j = plot_mean_and_var(xy, var_j[:, 0], var_j[:, 1], '$dim_1$',
                              '$dim_2$')
    plt.suptitle("$\mathbb{V}[\mathbf{J}] = diag(\Sigma_J)$")
    plt.savefig(save_name + 'gradient_variance.pdf', transparent=True)

    # axs = plot_mean_and_var(xy, mu, var)
    # for ax in axs:
    #     ax.quiver(xy[:, 0], xy[:, 1], var_j[:, 0], var_j[:, 1])
    # plt.suptitle("$\Sigma_j$")
    # plt.savefig(save_name + 'gradient_variance_quiver.pdf', transparent=True)
    return axs


def plot_metric_trace(xy,
                      G,
                      mu,
                      var,
                      save_name='../../images/visualise_metric/'):

    labels = ['$G(x)_{1,1}$', '$G(x)_{1,2}$', '$G(x)_{2,1}$', '$G(x)_{2,2}$']
    axs = plot_scatter_matrix(xy, G, labels)
    plt.suptitle("$G(x)$")
    plt.savefig(save_name + 'G(x).pdf', transparent=True)

    traceG = np.trace(G, axis1=1, axis2=2)
    fig, axs = plt.subplots(1, 1, figsize=(12, 4))
    plt.subplots_adjust(wspace=0, hspace=0)
    surf_traceG = plot_contour(xy, traceG, axs)
    cbar = fig.colorbar(surf_traceG, shrink=0.5, aspect=5, ax=axs)
    plt.title('Tr(G(x))')
    plt.savefig(save_name + 'trace(G(x)).pdf', transparent=True)

    # detG = np.array([np.linalg.det(G[i, :, :]) for i in range(G.shape[0])])
    # fig, axs = plt.subplots(1, 1, figsize=(12, 4))
    # plt.subplots_adjust(wspace=0, hspace=0)
    # surf_detG = plot_contour(xy, detG, axs)
    # cbar = fig.colorbar(surf_detG, shrink=0.5, aspect=5, ax=axs)
    # plt.title('det(G(x))')
    # plt.savefig(save_name + 'det(G(x)).pdf', transparent=True)

    # axs = plot_mean_and_var(xy, mu, var)
    # plt.suptitle("G(x)")
    # for ax in axs:
    #     ax.quiver(xy[:, 0], xy[:, 1], G[:, 0, 0], G[:, 1, 1])
    # plt.savefig(save_name + 'G(x)_quiver.pdf', transparent=True)
    return axs


def load_data_and_init_kernel_fake(filename):
    # Load kernel hyper-params and create kernel
    params = np.load(filename)
    l = params['l']  # [2]
    var = params['var']  # [1]
    X = params['x']  # [num_data x 2]
    a_mu = params['a_mu']  # [num_data x 1] mean of alpha
    a_var = params['a_var']  # [num_data x 1] variance of alpha
    kernel = DiffRBF(X.shape[1], variance=var, lengthscale=l, ARD=True)
    return X, a_mu, a_var, kernel


if __name__ == "__main__":

    X, a_mu, a_var, kernel = load_data_and_init_kernel_fake(
        filename='../saved_models/params_fake.npz')
    Y = a_mu

    import datetime
    from pathlib import Path
    date = datetime.datetime.now()
    date_str = str(date.day) + "-" + str(date.month) + "/" + str(
        date.time()) + "/"
    save_name = "../../images/visualise_metric/" + date_str
    Path(save_name).mkdir(parents=True, exist_ok=True)

    # plot original GP
    xy, xx, yy = create_grid(X, N=961)
    mu, cov = gp_predict(xy, X, a_mu, kernel)
    var = np.diag(cov).reshape(-1, 1)
    axs = plot_mean_and_var(xy, mu, var)
    plt.suptitle('Original GP')
    plt.savefig(save_name + 'original_gp.pdf', transparent=True)

    print('Calculating trace of metric, cov_j and mu_j...')
    G, mu_j, cov_j = vmap(calc_G_map, in_axes=(0, None, None, None))(xy, X, Y,
                                                                     kernel)
    print('Done calculating metric')
    # mu_j, var_j = gp_derivative_predict(xy, X, Y, kernel)
    var_j = vmap(np.diag, in_axes=(0))(cov_j)

    axs = plot_gradient(xy, mu_j, var_j, mu, var, save_name)

    axs = plot_metric_trace(xy, G, mu, var, save_name)

    plt.show()
