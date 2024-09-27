import win32com.client
import re
import json


class HFSSProjectHandler:
    def __init__(self):
        """
        初始化 HFSSProjectHandler 类，创建 AEDT COM 对象并获取桌面对象。
        """
        try:
            self.oAnsoftApp = win32com.client.Dispatch("Ansoft.ElectronicsDesktop")
            self.oDesktop = self.oAnsoftApp.GetAppDesktop()
            print("成功创建 COM 对象并获取桌面对象。")
        except Exception as e:
            print(f"初始化时发生错误: {e}")
            self.oDesktop = None
            self.oProject = None

    def open_project(self, file_path):
        """
        打开指定路径的 HFSS 项目文件。

        :param file_path: HFSS 项目文件的路径 (.aedt 文件)。
        """
        if self.oDesktop is None:
            print("无法打开项目，因为桌面对象未能成功初始化。")
            return

        try:
            self.oDesktop.OpenProject(file_path)
            self.oProject = self.oDesktop.GetActiveProject()

            if self.oProject is None:
                print("项目未能成功打开。")
            else:
                print(f"项目 '{self.oProject.GetName()}' 已成功打开。")
        except Exception as e:
            print(f"打开 HFSS 项目时发生错误: {e}")
            self.oProject = None

    def get_design_by_name(self, design_name):
        """
        根据名字获取设计对象。

        :param design_name: 设计的名字。
        :return: 返回指定名字的设计对象，如果不存在则返回 None。
        """
        if self.oProject is None:
            print("没有活动项目，无法获取设计。")
            return None

        try:
            oDesign = self.oProject.SetActiveDesign(design_name)
            if oDesign is None:
                print(f"未找到名字为 '{design_name}' 的设计。")
            else:
                print(f"设计 '{design_name}' 已成功激活。")
            return oDesign
        except Exception as e:
            print(f"获取设计 '{design_name}' 时发生错误: {e}")
            return None

    def get_excitation_name (self,oDesign):
        """
        获取模型

        :param oDesign: 设计对象
        :return: 激励名称
        """
        if oDesign is None:
            print("无效的设计对象，无法获取激励几何信息。")
            return None

        try:
            # 获取 BoundarySetup 模块
            oModule = oDesign.GetModule("BoundarySetup")

            # 获取所有激励的名称
            excitations = oModule.GetExcitations()
            return excitations

        except Exception as e:
            print(f"获取激励几何面顶点坐标时发生错误: {e}")
            return None

    def get_coordinate_fromface (self,faceid,oDesign):
        """
        通过faceID获取vertexID，通过vertexID获取坐标
        :param oDesign:设计对象
        :return: 坐标列表
        """
        oEditor = oDesign.SetActiveEditor("3D Modeler")

        vertices = oEditor.GetVertexIDsFromFace(faceid)
        vertex_coords = []

        for vertex_id in vertices:
            coords = oEditor.GetVertexPosition(vertex_id)
            vertex_coords.append(coords)
        vertex_coords_float = [(float(x), float(y), float(z)) for x, y, z in vertex_coords]

        return vertex_coords_float

    def close_project(self):
        """
        关闭当前打开的项目。
        """
        if self.oProject:
            try:
                self.oProject.Close()
                print(f"项目 '{self.oProject.GetName()}' 已成功关闭。")
            except Exception as e:
                print(f"关闭项目时发生错误: {e}")

    def close(self):
        """
        关闭 Ansoft Electronics Desktop 应用程序。
        """
        if self.oDesktop:
            try:
                self.oDesktop.Quit()
                print("AEDT 已关闭。")
            except Exception as e:
                print(f"关闭 AEDT 时发生错误: {e}")

def read_file(file_path):
    """读取文件内容"""
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def extract_waveport_sections(text):
    # 定义模式，匹配 oModule.AssignWavePort(
    pattern = r'oModule\.AssignWavePort\('
    matches = list(re.finditer(pattern, text))  # 找出所有匹配的起始位置

    results = []
    for match in matches:
        start_idx = match.start()  # 获取匹配的起始位置
        stack = ['(']  # 初始化堆栈，开始于第一个 '('
        i = match.end()  # 从匹配结束的位置开始遍历文本

        while i < len(text):
            char = text[i]

            if char == '(' or char == '[':
                stack.append(char)  # 遇到左括号 '(' 或 '['，压入堆栈
            elif char == ')' or char == ']':
                if stack and ((char == ')' and stack[-1] == '(') or (char == ']' and stack[-1] == '[')):
                    stack.pop()  # 遇到右括号，检查是否匹配堆栈顶部，匹配则弹出

            if not stack:  # 当堆栈为空时，表示匹配结束
                results.append(text[start_idx:i + 1])  # 提取匹配到的段落
                break

            i += 1

    return results

def extract_NAME(text):
    # 匹配 "NAME:x"
    pattern = r'"NAME:(\S+)"'  # \S+ 匹配非空字符
    match = re.search(pattern, text)  # 查找匹配

    if match:
        return match.group(1)  # 提取括号中的内容
    return None

def extract_Faces_value(text):
    # 匹配 "Faces:="  [x]，
    pattern = r'"Faces:="\s*,\s*\[(.*?)\]'  # 匹配 "Faces:=", 后面的 [7]
    match = re.search(pattern, text)  # 查找匹配

    if match:
        return match.group(1)  # 提取方括号中的内容
    return None

def get_coordinate_from_faceID(faceID):
    cooridinate = handler.get_coordinate_fromface(faceID, oDesign)
    converted_cooridinate = [list(item) for item in cooridinate]
    return converted_cooridinate

def pack_coordinate(file_path):
    file_content = read_file(file_path)
    matched_sections = extract_waveport_sections(file_content)
    matched_names = []
    matched_faces = []
    coordinates_fromintline = []
    coordinates = {}
    for section in matched_sections:
        matched_names.append(extract_NAME(section))
        matched_faces.append(extract_Faces_value(section))
        coordinates_fromintline.append(get_coordinates_fromscript(section))
    matched_faces_int = [int(num) for num in matched_faces]

    for i in range(len(matched_names)):
        coordinates_partA = get_coordinate_from_faceID(matched_faces_int[i])
        coordinates_partB = coordinates_fromintline[i]
        converten_partA = [tuple(item) for item in coordinates_partA]
        converten_partB = [tuple(item) for item in coordinates_partB]
        coordinates[matched_names[i]] = converten_partA
        coordinates[matched_names[i]] += converten_partB
    return coordinates

def get_coordinates_fromscript(text):
    pattern = r'("Start:="\s*,\s*\[(.*?)\])|("End:="\s*,\s*\[(.*?)\])'
    matches = re.findall(pattern, text)

    # 函数：提取数字并去除 "mm" 单位
    def extract_numbers(text):
        # 使用正则表达式找到所有的数字，并去除 "mm"
        numbers = re.findall(r'\b([\d\.]+)mm\b', text)
        # 将字符串数字转换为 float 类型
        return [float(number) for number in numbers]

    # 初始化列表
    start_list = []
    end_list = []
    return_list = []

    # 遍历匹配项，提取并转换数值
    for match in matches:
        result_text = match[1] if match[1] else match[3]
        if 'Start:=' in match[0] or 'Start:=' in match[2]:
            start_list = extract_numbers(result_text)
        elif 'End:=' in match[0] or 'End:=' in match[2]:
            end_list = extract_numbers(result_text)
    return_list.append(start_list)
    return_list.append(end_list)

    return return_list


def write_dict_to_json(data_dict, filename):
    # 将元组转换为列表，因为 JSON 不支持元组
    data_dict = {key: list(value) for key, value in data_dict.items()}

    # 写入 JSON 文件
    with open(filename, 'w') as json_file:
        json.dump(data_dict, json_file, indent=4)

    print(f"字典已成功写入 {filename} 文件。")


if __name__ == "__main__":
    # 创建 HFSS 项目处理类的实例
    handler = HFSSProjectHandler()

    # HFSS 文件路径
    hfss_file_path = r"D:\Ansys Electronics 2021 R2\Project\Face3.aedt"
    handler.open_project(hfss_file_path)

    # 获取指定名字的设计
    design_name = "HFSSDesign1"
    oDesign = handler.get_design_by_name(design_name)

    # 获得激励名字
    excitationname = handler.get_excitation_name(oDesign)

    #通过脚本获取相应faceID
    file_path = "D:\Ansys Electronics 2021 R2\Project\Face3.aedtresults\Face3_script.py"
    coordinates = pack_coordinate(file_path)

    print(coordinates)

    # 关闭项目和 AEDT 应用程序
    handler.close_project()
    handler.close()

    # 写成json文件
    filename = 'testfile.json'
    write_dict_to_json(coordinates, filename)