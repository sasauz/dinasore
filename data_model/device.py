from data_model import utils


class Device(utils.DiacInterface):

    def __init__(self, ua_peer):
        utils.DiacInterface.__init__(self, ua_peer, 'DeviceSet')
        self.state = ''

    def from_xml(self, root_xml):
        """
        device               -> fb
            description.name -> fb_type
        methods              -> input_events
        data_vars            -> output_vars
            variable.name    -> output_var_name

        :param root_xml:
        """
        self.subs_id = root_xml.attrib['id']

        # creates the header opc-ua (description, ...) of this device
        self.__create_header(root_xml)

        # creates the fb inside the configuration
        self.ua_peer.config.create_virtualized_fb(self.fb_name, self.fb_type, self.update_variables)

        for item in root_xml:
            # splits the tag in these 3 camps
            uri, ignore, tag = item.tag[1:].partition("}")

            if tag == 'variables':
                # link opc-ua variables in fb input variable
                self.__create_variables(item)

            elif tag == 'methods':
                # link opc-ua methods in fb methods
                self.__create_methods(item)

            elif tag == 'subscriptions':
                self.__create_context_links(item)

        # link variable to the start fb (sensor to init fb)
        if root_xml.attrib['type'] == 'SENSOR':
            self.ua_peer.config.create_connection('{0}.{1}'.format('START', 'COLD'),
                                                  '{0}.{1}'.format(self.fb_name, 'Init'))

    def from_diac(self, fb):
        pass

    def __create_header(self, header_xml):
        # creates the device object
        for variables in header_xml:
            # splits the tag in these 3 camps
            uri, ignore, tag = variables.tag[1:].partition("}")

            if tag == 'variables':
                for var in variables:
                    if var.attrib['name'] == 'Description':
                        # creates the device properties
                        for element in var[0]:
                            # creates the opc-ua object
                            if element.attrib['id'] == 'Name':
                                self.fb_name = element.text
                                # creates the device object
                                self.create_base_object(self.fb_name)

                            # creates the fb
                            elif element.attrib['id'] == 'SourceType':
                                self.fb_type = element.text
                                # creates the respective property
                                utils.default_property(self.ua_peer, self.base_idx, self.base_path,
                                                       property_name='SourceType', property_value=self.fb_type)

                            # creates the state
                            elif element.attrib['id'] == 'SourceState':
                                self.state = element.text
                                # creates the respective property
                                utils.default_property(self.ua_peer, self.base_idx, self.base_path,
                                                       property_name='SourceState', property_value=self.state)
                        break
                break

            # create the id property
            utils.default_property(self.ua_peer, self.base_idx, self.base_path, 'ID', header_xml.attrib['id'])

    def __create_methods(self, methods_xml):
        # creates the methods folder
        folder_idx, methods_path, methods_list = utils.default_folder(self.ua_peer, self.base_idx,
                                                                      self.base_path, self.base_path_list, 'Methods')
        for method in methods_xml:
            method_name = method.attrib['name']

            # gets the created fb
            fb = self.ua_peer.config.get_fb(self.fb_name)

            method2call = utils.Method2Call(method_name, fb, self.ua_peer)
            # parses the method from the xml
            method2call.from_xml(method)
            # virtualize (opc-ua) the method
            method2call.virtualize(folder_idx, methods_path, method2call.method_name)

    def __create_variables(self, vars_xml):
        # creates the variables folder
        folder_idx, vars_path, vars_list = utils.default_folder(self.ua_peer, self.base_idx,
                                                                self.base_path, self.base_path_list, 'Variables')
        # creates the opc-ua variables and links them
        for var in vars_xml:
            if var.attrib['name'] != 'Description':
                # create the variable
                var_idx, var_object = self.create_variable(var, folder_idx, vars_path)
                # adds the variable to the dictionary
                self.ua_variables[var.attrib['name']] = var_object

    def __create_context_links(self, links_xml):
        # creates the subscriptions folder
        folder_idx, subs_path, subs_list = utils.default_folder(self.ua_peer, self.base_idx,
                                                                self.base_path, self.base_path_list, 'Subscriptions')
        for subs in links_xml:
            # context connections between sensors/actuators and components/equipments
            pass