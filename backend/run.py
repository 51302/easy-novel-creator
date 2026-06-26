#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
*********************************************************************************
@Time     : 2025/6/26 12:46
@Author   : liu23
@File     : run.py
@Software : PyCharm
@Desc     : AI Novel Creator 后端服务启动脚本
*********************************************************************************
"""
import uvicorn

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
