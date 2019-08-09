import unittest
import dash_utils as du
import seaborn as sns
import dash_core_components as dcc


class TestUtils(unittest.TestCase):

    def setUp(self):
        self.df = sns.load_dataset('titanic')

    def test_column(self):
        col = du.column([])
        self.assertTrue(col.className == 'five columns')

    def test_row(self):
        row = du.row([])
        self.assertTrue(row.className == 'row')

    def test_figure_grid_odd(self):

        grid = du.figure_grid(3)
        self.assertTrue(len(grid) == 3)

    def test_figure_grid_even(self):

        grid = du.figure_grid(2)
        self.assertTrue(len(grid) == 2)

    def test_figure_grid_childs(self):

        grid = du.figure_grid(0, ['one', 'two'])
        self.assertTrue(len(grid) == 2)

    def test_control_grid(self):

        grid = du.control_grid(['one', 'two', 'three'])
        self.assertTrue(len(grid) == 3)

    def test_return_selection(self):
        pass

    def test_make_histogram_plain(self):

        hist = du.make_histogram(self.df, 'age', 10)
        self.assertIsInstance(hist, dict) and self.assertTrue('data' in hist.keys())

    def test_make_histogram_hue(self):

        hist = du.make_histogram(self.df, 'age', 10, color_filter='pclass')
        self.assertTrue(len(hist['data']) == 3)

    def test_make_table(self):

        table = du.make_table(columns=['pclass', 'age'], data=self.df)
        self.assertTrue(len(table.columns) == 2)

    def test_make_scatter_plain(self):

        scat = du.make_scatter(self.df, 'age', 'fare')
        self.assertIsInstance(scat, dict) and self.assertTrue('data' in scat.keys())

    def test_make_scatter_hue(self):

        scat = du.make_scatter(self.df, 'age', 'fare', color_filter='pclass')
        self.assertTrue(len(scat['data']) == 3)

    def test_make_heatmap_plain(self):

        heatmap = du.make_heatmap(self.df.corr().values,  10, 10, self.df.corr().values,
                                  colorscale=[0, 10], cmap=None, layout_kwargs={})
        self.assertIsInstance(heatmap, dict) and self.assertTrue('data' in heatmap.keys())

    def test_make_go_list(self):

        go_list = du.make_go_list(['Heatmap', 'Scatter'])
        self.assertTrue(len(go_list) == 2)

    def test_make_control_list(self):

        control_list = du.make_control_list([{"name": "Dropdown", "args": {"options":[1,2,3],"value":None}}])
        self.assertIsInstance(control_list[0], dcc.Dropdown)

    def test_matplotlib_to_plotly(self):
        from matplotlib import cm
        cmap = cm.get_cmap('viridis')
        colorscale = du.matplotlib_to_plotly(cmap, 3)
        self.assertTrue(len(colorscale) == 3)

    def test_data_profile_tables(self):

        table = du.data_profile_tables({})
        self.assertTrue(len(table.columns) == 2) and self.assertTrue(table.data == [])
