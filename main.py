#!/bin/sh python
#-.- encoding: utf-8 -.-
import datetime

import kivy
from kivy.adapters.dictadapter import DictAdapter
from kivy.app import App
from kivy.properties import StringProperty
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.listview import ListItemButton, ListView
from kivy.uix.popup import Popup
from kivy.uix.tabbedpanel import TabbedPanelHeader, TabbedPanel
from kivy.uix.textinput import TextInput
import communicate

kivy.require('1.8.0')

class PartnerUpdate(TabbedPanel):
    def __init__(self, **kwargs):
        super(PartnerUpdate, self).__init__(**kwargs)
        self.select_partner_tab = TabbedPanelHeader(text = 'Children')
        self.communication_tab = TabbedPanelHeader(text = 'Communication')
        self.add_widget(self.select_partner_tab, 0)
        self.add_widget(self.communication_tab, 0)
        self.content.do_layout()

    def get_partnerlist(self):
        return "Hei og hopp"

    def switch_to(self, header, date = datetime.date.today()):
        """
        if header is self.reg_tab:
        self.crew_tab.content = CrewList(self)
        :param header:
        :param date:
        :return:
        """
        super(PartnerUpdate, self).switch_to(header)

class PartnerUpdateApp(App):
    def build(self):
        return PartnerUpdate()


partner_attributes = ['name', 'phone', 'street', 'street2', 'zip', 'city', 'school', 'school_class', 'parent_1', 'parent_2']

partner_datatypes = ['text',  'text',   'text',   'text',   'text', 'text', 'text', 'text', 'text', 'text']
partner_columns = zip(partner_attributes, partner_datatypes)



class PartnerDetailView(GridLayout):
    child_name = StringProperty('', allownone=True)

    def __init__(self, parent_o, **kwargs):
        kwargs['cols'] = 2
        self.parent_o = parent_o
        self.child_name = kwargs.get('child_name', '')
        super(PartnerDetailView, self).__init__(**kwargs)
        if self.child_name:
            self.redraw()


    def redraw(self, *args):
        self.clear_widgets()
        if self.child_name and self.child_name in self.parent_o.partner_data:
            self.add_widget(Label(text="Name:", halign='right'))
            self.add_widget(Label(text=self.child_name, height=25))
            for attribute in partner_attributes:
                self.add_widget(Label(text="{0}:".format(attribute),
                                      halign='right'))
                #print "REDRAW", self.child_name, attribute, self.parent_o.partner_data
                if attribute in self.parent_o.partner_data[self.child_name]:
                    pdata = self.parent_o.partner_data[self.child_name]
                    if pdata[attribute]:
                        value = pdata[attribute].encode('utf-8')
                    else:
                        value = ''
                else:
                    value = ''
                c = TextInput(text=value, height='29px',size_hint_y=None, multiline=False)
                c.attribute = attribute
                c.bind(text = self.update_textinput)
                self.add_widget(c)

                #c.size_hint_y = 0.1

                c.set_height = '25px'

    def update_textinput(self, instance, value):
        if not hasattr(instance, 'attribute'):
            raise AttributeError('The widget should have a attribute set...')
        attribute = instance.attribute
        print "UPDATED", self.child_name, attribute, instance.text, value
        communicate.update_attribute(self.child_name, attribute, value)
        instance.background = [0,1,0,0]


    def partner_changed(self, list_adapter, **args):
        self.widgets = {}
        if len(list_adapter.selection) == 0:
            self.child_name = None
        else:
            selected_object = list_adapter.selection[0]

            if type(selected_object) is str:
                self.child_name = selected_object
            else:
                self.child_name = selected_object.text
        self.redraw()

class CommunicateContent(GridLayout):
    widgets = {}
    parameters = [
        ('Server', 'localhost:8069'),
        ('User', 'admin'),
        ('Password', 'admin')
    ]

    def __init__(self, parent_o, items, **kwargs):
        kwargs['cols'] = 2
        super(CommunicateContent, self).__init__(**kwargs)
        self.size_hint_y = None
        self.parent_o = parent_o

        for param in self.parameters:
            self.add_widget(Label(text=param[0],
                                      halign='right'))

            c = TextInput(text=str(param[1]), height='27px',size_hint_y=None, multiline=False)

            c.bind(text = self.update_parameter)
            self.add_widget(c)
            self.widgets[c] = param[0]
            self.update_parameter(c, str(param[1]))

    def update_parameter(self, instance, value):
        print "UPDATE_PARAMETER", instance, value, self.widgets[instance]
        setattr(self.parent_o, self.widgets[instance].lower(), value)
        print "UPDATED", self.parent_o, self.widgets[instance]
        print "YEAH?", getattr(self.parent_o, 'server')





class PartnerUpdateView(GridLayout):

    partner_data = {'Child 1' : {'name' : 'Child 1',
                             'street' : None,
                             'street2' : None,
                             'type' : 'Unknown',
                             'zip' : None,
                             'city' : 'Some Village',
                             'phone' : '22 55 55 55'}}

    def __init__(self, **kwargs):
        kwargs['cols'] = 2
        super(PartnerUpdateView, self).__init__(**kwargs)


        self.list_item_args_converter = \
                lambda row_index, rec: {'text': rec['name'],
                                        'size_hint_y': None,
                                        'height': 25}

        self.dict_adapter = DictAdapter(sorted_keys=sorted(self.partner_data.keys()),
                                   data=self.partner_data,
                                   args_converter=self.list_item_args_converter,
                                   selection_mode='single',
                                   allow_empty_selection=False,
                                   cls=ListItemButton)

        self.master_list_view = ListView(adapter=self.dict_adapter,
                                    size_hint=(.3, 1.0))

        self.add_widget(self.master_list_view)

        self.popup = self.make_comm_popup()

        detail_container = AnchorLayout()
        detail_view = PartnerDetailView(self,
                fruit_name=self.dict_adapter.selection[0].text,
                size_hint=(.7, None))
        detail_container.add_widget(detail_view)

        self.dict_adapter.bind(on_selection_change=detail_view.partner_changed)

        communicate_button_layout = AnchorLayout(anchor_y = 'bottom', size_hint = (.7, None))
        communicate_button = Button(text = 'Communication', size_hint_y=None,height=25)
        communicate_button.bind(on_press = self.popup.open)
        communicate_button_layout.add_widget(communicate_button)
        self.add_widget(detail_container)
        self.add_widget(communicate_button_layout)

    def make_comm_popup(self):

        prms = {} # TODO add server parameters from DB
        cont = BoxLayout(orientation = 'vertical')
        cont.add_widget(CommunicateContent(self, prms))

        gl = GridLayout(cols=2)
        fetch_button = Button(text = 'Fetch data', size_hint_y=None, height=25)
        fetch_button.bind(on_press = self.fetch_data)
        send_button = Button(text = 'Send data', size_hint_y=None, height=25)
        send_button.bind(on_press = self.send_data)
        gl.add_widget(fetch_button)
        gl.add_widget(send_button)
        cont.add_widget(gl)


        return Popup(title = 'Communicate', content = cont, size_hint=(0.6, None), height=200)

    def fetch_data(self, instance):
        self.popup.dismiss()
        communicate.fetch_partners(self.server, self.user, self.password)
        self.partner_data = communicate.get_partners_from_db()
        print "DATA", self.dict_adapter.data.keys()
        for d in self.dict_adapter.data.items():
            print "HEI", d


        #self.partner_data = {'hei' : {'name': 'hei'}}
        self.dict_adapter.sorted_keys = sorted(self.partner_data.keys())
        #self.dict_adapter.data = [('hei', {'name' : 'hei'})]
        self.dict_adapter.data = self.partner_data

        #self.dict_adapter = DictAdapter(sorted_keys=sorted(partner_data.keys()),
        #                           data=partner_data,
        #                           args_converter=self.list_item_args_converter,
        #                           selection_mode='single',
        #                           allow_empty_selection=False,
        #                           cls=ListItemButton)
        #self.master_list_view = self.dict_adapter
        #self.dict_adapter.sorted_keys = sorted(partner_data.keys())
        #self.dict_adapter.data = partner_data

        #self.add_widget(self.master_list_view)


    def send_data(self, instance):
        self.popup.dismiss()
        communicate.send_partners(self.server, self.user, self.password)

if __name__ == '__main__':

    from kivy.base import runTouchApp

    master_detail = PartnerUpdateView(width=800)

    runTouchApp(master_detail)
