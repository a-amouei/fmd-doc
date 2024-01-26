from pygments.lexers.c_cpp import CLexer
from pygments.token import Token
from pygments.style import Style

class CFMDStyle(Style):
    background_color = "#fafafa"

    styles = {
        Token.FMDType:                   "bold #0000EE",
        Token.FMDFunction:               "#500050",
        Token.FMDConstant:               "bold #444444",
        Token.Whitespace:                "#bbbbbb",
        Token.Comment:                   "#3D7B7B",
        Token.Comment.Preproc:           "noitalic #9C6500",

        Token.Keyword:                   "bold #F000F0",
        Token.Keyword.Pseudo:            "nobold",
        Token.Keyword.Type:              "nobold #0000FF",

        Token.Operator:                  "",
        Token.Operator.Word:             "",

        Token.Name.Builtin:              "#00A0A0",
        Token.Name.Function:             "",
        Token.Name.Class:                "bold #0000FF",
        Token.Name.Namespace:            "bold #0000FF",
        Token.Name.Exception:            "bold #CB3F38",
        Token.Name.Variable:             "#19177C",
        Token.Name.Constant:             "#880000",
        Token.Name.Label:                "#767600",
        Token.Name.Entity:               "bold #717171",
        Token.Name.Attribute:            "#687822",
        Token.Name.Tag:                  "bold #008000",
        Token.Name.Decorator:            "#AA22FF",

        Token.String:                    "#FF4400",
        Token.Number:                    "#008000",

        Token.Generic.Heading:           "bold #000080",
        Token.Generic.Subheading:        "bold #800080",
        Token.Generic.Deleted:           "#A00000",
        Token.Generic.Inserted:          "#008400",
        Token.Generic.Error:             "#E40000",
        Token.Generic.Emph:              "",
        Token.Generic.Strong:            "bold",
        Token.Generic.EmphStrong:        "bold",
        Token.Generic.Prompt:            "bold #000080",
        Token.Generic.Output:            "#313131",
        Token.Generic.Traceback:         "#04D",

        Token.Error:                     "border:#FF0000"
    }

class CFMDLexer(CLexer):
    fmd_types = ['fmd_handle_t', 'fmd_t', 'fmd_event_t', 'fmd_params_t',
                 'fmd_event_params_timer_tick_t', 'fmd_real_t', 'fmd_string_t']
    fmd_functions = ['fmd_create', 'fmd_setEventHandler', 'fmd_io_printf',
                     'fmd_dync_getTime', 'fmd_matt_getTemperature', 'fmd_matt_getTotalEnergy',
                     'fmd_matt_saveConfiguration', 'fmd_timer_makeSimple', 'fmd_box_setSize',
                     'fmd_box_setPBC', 'fmd_box_setSubdomains', 'fmd_matt_setAtomKinds',
                     'fmd_pot_lj_apply', 'fmd_matt_makeCuboidFCC', 'fmd_dync_equilibrate',
                     'fmd_io_saveState', 'fmd_proc_getWallTime', 'fmd_free']
    fmd_constants = ['FMD_EVENT_TIMER_TICK']

    def get_tokens_unprocessed(self, text, stack=('root',)):
        for index, token, value in CLexer.get_tokens_unprocessed(self, text, stack):
            if token is Token.Name and value in self.fmd_types:
                yield index, Token.FMDType, value
            elif token is Token.Name and value in self.fmd_functions:
                yield index, Token.FMDFunction, value
            elif token is Token.Name and value in self.fmd_constants:
                yield index, Token.FMDConstant, value
            else:
                yield index, token, value

def setup(app):
    app.add_lexer('cfmd', CFMDLexer)
