import os
import regressions
import plotfuncs
import getdata
import rapport_data

def main():
	dframe = getdata.data_main()
	plot_target_dir = os.path.join(os.getcwd(), 'plots')
	plotfuncs.plot_and_save_all(dframe, plot_target_dir)	
	
	reg_results =  regressions.day_contrib_reg(dframe,'infection')
	regressions.export_regression_results(reg_results)
	
	testing_df, rapport_name = rapport_data.main()
	plotfuncs.plot_testing_data(testing_df, rapport_name, plot_target_dir)
	getdata.export_data(dframe)

if __name__== "__main__":
	main()


