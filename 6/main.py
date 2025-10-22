#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@File    :   test_case_generator.py
@Time    :   2025/01/01 00:00:00
@Author  :   CrissChan 
@Version :   2.0
@Desc    :   基于正交试验的测试用例生成器 - 重构版本
'''

import os
import json
# import itertools
from typing import List, Dict, Tuple, Any

try:
    from langchain_ollama import OllamaLLM as Ollama
except ImportError:
    from langchain_community.llms import Ollama


class TestCaseGenerator:
    """测试用例生成器类"""
    
    def __init__(self, model: str = "gpt-oss:120b-cloud", base_url: str = None):
        """
        初始化测试用例生成器
        
        Args:
            model: Ollama模型名称
            base_url: Ollama服务地址
        """
        self.model = model
        self.base_url = base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.llm = None
        self._init_llm()
    
    def _init_llm(self) -> bool:
        """初始化Ollama LLM"""
        try:
            self.llm = Ollama(
                model=self.model,
                base_url=self.base_url,
                temperature=0.1,
                top_p=0.9,
                num_ctx=2048
            )
            return True
        except Exception as e:
            print(f"❌ 无法连接到Ollama服务: {e}")
            print(f"请确保Ollama服务正在运行: ollama serve")
            print(f"请确保{self.model}模型已下载: ollama pull {self.model}")
            return False
    
    def _parse_boundary_response(self, content: str) -> List[str]:
        """解析边界值响应"""
        try:
            # 先尝试eval解析（处理表达式如 "a" * 6）
            if '[' in content and ']' in content:
                start = content.find('[')
                end = content.rfind(']') + 1
                array_str = content[start:end]
                try:
                    result = eval(array_str)
                    if isinstance(result, list):
                        return result
                except Exception as e:
                    print(f"eval解析失败: {e}")
            
            # 尝试JSON解析
            cleaned_content = content.strip()
            if cleaned_content.startswith('[') and cleaned_content.endswith(']'):
                return json.loads(cleaned_content)
            
            # 尝试正则表达式提取引号内的内容
            import re
            matches = re.findall(r'"([^"]*)"', content)
            if matches:
                return matches
                
        except Exception as e:
            print(f"⚠️ 解析边界值失败: {e}, 内容: {content[:100]}...")
        
        return []
    
    def generate_boundary_values(self, parameter_descriptions: List[str]) -> List[List[str]]:
        """
        生成参数边界值
        
        Args:
            parameter_descriptions: 参数描述列表
            
        Returns:
            边界值列表
        """
        if not self.llm:
            print("❌ LLM未初始化")
            return []
        
        boundary_values = []
        delimiter = "####"
        
        for desc in parameter_descriptions:
            prompt = f"""{delimiter}你是一名资深测试工程师。
{delimiter}设计参数的边界值: {desc}
{delimiter}边界值要包含满足要求和不满足要求的内容，直接返回字符串数组，格式如：["value1", "value2", "value3"]
{delimiter}不要返回python代码，不要包含任何注释。"""
            
            try:
                print(f"🔄 正在生成参数边界值: {desc}")
                response = self.llm.invoke(prompt)
                values = self._parse_boundary_response(response)
                boundary_values.append(values)
                print(f"✅ 生成边界值: {values}")
            except Exception as e:
                print(f"❌ 生成边界值失败: {e}")
                boundary_values.append([])
        
        return boundary_values
    
    def generate_orthogonal_table(self, levels: List[int]) -> List[Tuple[int, ...]]:
        """
        生成正交表
        
        Args:
            levels: 各因素的水平数列表
            
        Returns:
            正交表数据
        """
        i=1
        prompt = f"计算一个正交表，因素数是{len(levels)}，"
        for level in levels:
            prompt+=f"第{i}个因素，水平数是{level}，"
            i+=1
        prompt+=f"强度是2，只返回计算结果的二维数组，不返回其他内容。"
        print(prompt)
        response = self.llm.invoke(prompt)
        list = json.loads(response)
        # response = response.replace("```R\n", "").replace("```\n", "").replace("```", "").replace("R\n", "").replace("R", "")
        # response = response.split("\n")
        # response = [list(map(int, row.split())) for row in response]

        return list
        # return list(itertools.product(*[range(1, level + 1) for level in levels]))
    
    def generate_test_cases(self, parameter_descriptions: List[str]) -> List[Tuple[str, ...]]:
        """
        生成测试用例
        
        Args:
            parameter_descriptions: 参数描述列表
            
        Returns:
            测试用例列表
        """
        # 1. 生成边界值
        boundary_values = self.generate_boundary_values(parameter_descriptions)
        
        if not boundary_values or any(not values for values in boundary_values):
            print("❌ 边界值生成失败")
            return []
        
        # 2. 生成正交表
        levels = [len(values) for values in boundary_values]
        orthogonal_table = self.generate_orthogonal_table(levels)
        
        print(f"📊 正交表: {orthogonal_table}")
        
        # 3. 生成测试用例
        test_cases = []
        for row in orthogonal_table:
            test_case = tuple(
                boundary_values[i][row[i] - 1] 
                for i in range(len(row))
            )
            test_cases.append(test_case)
        
        return test_cases


def main():
    """主函数"""
    print("测试用例生成器启动")
    
    # 参数描述
    parameters = [
        "username是一个系统的用户名，string类型，长度限制6个字符，不能为空",
        "password是一个系统用户的密码，string类型，长度限制8个字符，不能为空，至少有一个大写字母，一个数字，一个特殊字符"
    ]
    
    # 创建生成器
    generator = TestCaseGenerator()
    
    if not generator.llm:
        print("生成器初始化失败")
        return
    
    # 生成测试用例
    test_cases = generator.generate_test_cases(parameters)
    
    if test_cases:
        print(f"\n生成测试用例 {len(test_cases)} 个:")
        for i, case in enumerate(test_cases, 1):
            print(f"  {i:2d}. {case}")
    else:
        print("测试用例生成失败")


if __name__ == "__main__":
    main()
