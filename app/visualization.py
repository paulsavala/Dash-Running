from flask import render_template, flash, redirect, url_for, request
from app import app, db
from flask_login import current_user, login_required
from app.models import User, Run
from bokeh.plotting import figure
from bokeh.embed import components
import numpy as np
import pandas as pd

def bokeh_test_components(gradient=0):
    #minutes = app.config['MAX_MINUTES']
    minutes = 5
    time = np.arange(1, 60*minutes+1)

    test_msm_dir = app.config['MSM_FOLDER']
    test_msm = pd.read_csv(test_msm_dir + '2018-02-02/1.csv')

    speed_at_gradient = test_msm[str(gradient)][1:]

    p = figure(title="Speed at Gradient", plot_height=300, plot_width=600, y_range=(2,5))
    p.line(x = time, y = speed_at_gradient)
    script, div = components(p)
    return script, div
