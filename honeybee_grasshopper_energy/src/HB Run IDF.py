# Honeybee: A Plugin for Environmental Analysis (GPL)
# This file is part of Honeybee.
#
# Copyright (c) 2019, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Honeybee; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Run an IDF file through EnergyPlus.

-
    Args:
        _idf: Path to an IDF file as a text string. This can also be a list of
            IDF files.
        _epw_ile: Path to an .epw file as a text string.
        parallel_: Set to "True" to run execute simulations of multiple IDF files
            in parallel, which can greatly increase the speed of calculation but
            may not be desired when other processes are running. If False, all
            EnergyPlus simulations will be be run on a single core. Default: False.
        run_: Set to "True" to run the IDF through EnergyPlus.
    
    Returns:
        report: Check here to see a report of the EnergyPlus run.
        sql: The file path of the SQL result file that has been generated on your
            machine.
        zsz: Path to a .csv file containing detailed zone load information recorded
            over the course of the design days.
        rdd: The file path of the Result Data Dictionary (.rdd) file that is
            generated after running the file through EnergyPlus.  This file
            contains all possible outputs that can be requested from the EnergyPlus
            model.  Use the Read Result Dictionary component to see what outputs
            can be requested.
        html: The HTML file path of the Summary Reports. Note that this will be None
            unless the input _sim_par_ denotes that an HTML report is requested and
            run_ is set to True.
"""

ghenv.Component.Name = 'HB Run IDF'
ghenv.Component.NickName = 'RunIDF'
ghenv.Component.Message = '0.1.1'
ghenv.Component.Category = 'HB-Energy'
ghenv.Component.SubCategory = '5 :: Simulate'
ghenv.Component.AdditionalHelpFromDocStrings = '4'

import os
import System.Threading.Tasks as tasks

try:
    from honeybee_energy.run import run_idf
    from honeybee_energy.result.err import Err
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_energy:\n\t{}'.format(e))

try:
    from ladybug_rhino.grasshopper import all_required_inputs, give_warning
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))

def run_idf_and_report_errors(i):
    """Run an IDF file through EnergyPlus and report errors/warnings on this component."""
    idf = _idf[i]
    sql_i, zsz_i, rdd_i, html_i, err_i = run_idf(idf, _epw_file)

    # report any errors on this component
    if err_i is not None:
        err_obj = Err(err_i)
        err_objs.append(err_obj)
        for warn in err_obj.severe_errors:
            give_warning(ghenv.Component, warn)
        for error in err_obj.fatal_errors:
            raise Exception(error)

    # append everything to the global lists
    sql.append(sql_i)
    zsz.append(zsz_i)
    rdd.append(rdd_i)
    html.append(html_i)
    err.append(err_i)


if all_required_inputs(ghenv.Component) and _run:
    # global lists of outputs to be filled
    sql, zsz, rdd, html, err, err_objs = [], [], [], [], [], []

    # run the IDF files through E+
    if parallel_:
        tasks.Parallel.ForEach(range(len(_idf)), run_idf_and_report_errors)
    else:
        for i in range(len(_idf)):
            run_idf_and_report_errors(i)

    # print out error report if it's only one
    # otherwise it's too much data to be read-able
    if len(err_objs) == 1:
        print(err_objs[0].file_contents)
