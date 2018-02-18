from flask import render_template, flash, redirect, url_for, request
from app import app, db
from flask_login import current_user, login_required
from app.models import User, Run
from bokeh.plotting import figure
from bokeh.embed import components
import numpy as np
import pandas as pd

def bokeh_test_components(msm, gradient=0):
    #minutes = app.config['MAX_MINUTES']
    minutes = 5
    time = np.arange(1, 60*minutes+1)

    speed_at_gradient = msm[str(gradient)][1:]

    p = figure(title="Speed at Gradient", plot_height=600, plot_width=890, y_range=(2,5))
    p.line(x = time, y = speed_at_gradient)
    script, div = components(p)
    return script, div
