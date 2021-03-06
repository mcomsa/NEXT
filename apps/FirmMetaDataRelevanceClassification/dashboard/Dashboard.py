import json
import numpy
import numpy.random
from datetime import datetime
from datetime import timedelta
import next.utils as utils
from next.apps.AppDashboard import AppDashboard
from apps.WebsiteRelevanceClassification.algs import vw_api
# import next.database_client.DatabaseAPIHTTP as db
# import next.logging_client.LoggerHTTP as ell

class MyAppDashboard(AppDashboard):

    def __init__(self,db,ell):
        AppDashboard.__init__(self, db, ell)

    def test_error_multiline_plot(self, app, butler):
        """
        Description: Returns multiline plot where there is a one-to-one mapping lines to
        algorithms and each line indicates the error on the validation set with respect to number of reported answers

        Expected input:
          None

        Expected output (in dict):
          (dict) MPLD3 plot dictionary
        """
        print('\n in multi line plot functino')
        args = butler.experiment.get(key='args')
        alg_list = args['alg_list']
        test_alg_label = alg_list[0]['test_alg_label']

        test_queries, didSucceed, message = butler.db.get_docs_with_filter(app.app_id+':queries',{'exp_uid':app.exp_uid, 'alg_label':test_alg_label})


        print('\n in multi line plot function 2')
        test_S = [(query['target_index'], query['target_label'])
                            for query in test_queries
                            if 'target_index' in query.keys()]

        #targets = butler.targets.get_targetset(app.exp_uid)
        #targets = sorted(targets,key=lambda x: x['target_id'])
        #target_features = []

        #for target_index in range(len(targets)):
        #    target_vec = targets[target_index]['meta']['features']
        #    target_vec.append(1.)
        #    target_features.append(target_vec)

        x_min = numpy.float('inf')
        x_max = -numpy.float('inf')
        y_min = numpy.float('inf')
        y_max = -numpy.float('inf')
        list_of_alg_dicts = []

        for algorithm in alg_list:
            print('\n doing something for :', algorithm)
            alg_label = algorithm['alg_label']
            list_of_log_dict,didSucceed,message = self.ell.get_logs_with_filter(app.app_id+':ALG-EVALUATION',{'exp_uid':app.exp_uid, 'alg_label':alg_label})
            list_of_log_dict = sorted(list_of_log_dict, key=lambda item: utils.str2datetime(item['timestamp']) )
            x = []
            y = []

            for item in list_of_log_dict:
                print('\n calculating ... :', algorithm)
                num_reported_answers = item['num_reported_answers']
                precision = item['precision']

                err = int(precision*100)
                x.append(num_reported_answers)
                y.append(err)

            # this would be taken from a call to get_responses on
            #debug: proves we can retrive model precision w/in context of NextML
            x = numpy.argsort(x)
            x = [x[i] for i in x]
            y = [y[i] for i in x]

            alg_dict = {}
            alg_dict['legend_label'] = alg_label
            alg_dict['x'] = x
            alg_dict['y'] = y
            try:
                x_min = min(x_min,min(x))
                x_max = max(x_max,max(x))
                y_min = min(y_min,min(y))
                y_max = max(y_max,max(y))
            except:
                pass

            list_of_alg_dicts.append(alg_dict)

        import matplotlib.pyplot as plt
        import mpld3

        width = 0.8
        fig, ax = plt.subplots(subplot_kw=dict(axisbg='#EEEEEE'))
        for alg_dict in list_of_alg_dicts:
            ax.plot(alg_dict['x'],alg_dict['y'],label=alg_dict['legend_label'])
        ax.set_xlabel('Number of held out examples (#)')
        ax.set_ylabel('Accuracy (%)')
        ax.set_xlim([x_min,x_max])
        ax.set_ylim([y_min-width,y_max+width])
        ax.grid(color='white', linestyle='solid')
        ax.set_title('Website Relevance Accuracy on Held Out Examples (higher is better)' , size=14)
        legend = ax.legend(loc=2,ncol=3,mode="expand")
        for label in legend.get_texts():
            label.set_fontsize('small')
        plot_dict = mpld3.fig_to_dict(fig)
        plt.close()

        return plot_dict
