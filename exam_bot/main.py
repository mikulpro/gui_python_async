from interactive_user_interface import Tk_extended

GUI = Tk_extended()
GUI.mainloop_extended()

"""
def cog_loader(root): #, input=None):
    while True:
        try:
            if input is None:
                for subcog in root.core.snapped_to:
                    root.activate_cog(subcog)
                    for sub_subcog in subcog.snapped_to:
                        #self.cog_loader(sub_subcog)
                        root.activate_cog(sub_subcog)
            else:
                for subcog in input.snapped_to:
                    root.activate_cog(subcog)
        except:
            pass # pro preteceni rekurze
"""

"""
cog_loader_thread = threading.Thread(target=cog_loader(GUI))
GUI.start_cog_loader(cog_loader_thread)
"""