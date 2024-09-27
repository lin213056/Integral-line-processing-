1.在HFSS里建模的时候打开python脚本录制
2.将ObtainCoordinatesThroughFace ID.py，DeterminePointLineRelationship.py放在一个文件夹里
3.使用前关闭HFSS窗口
4.使用时更改变量名：
	文件ObtainCoordinatesThroughFace ID.py：
		250行：hfss_file_path -> 更改成你的HFSS文件的路径；
		254行：design_name -> 更改成你的设计的名字；
		261行：file_path -> 更改成你录制的python脚本的路径（一半在HFSS文件同一个地址下）
	文件DeterminePointLineRelationship.py：
		104行：keyname -> 更改成你想要计算的激励的名字