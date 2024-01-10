import setuptools

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setuptools.setup(
    name="nonebot-plugin-mcqq",
    version="2.5.3",
    author="17TheWord",
    author_email="17theword@gmail.com",
    description="基于NoneBot的QQ群聊与Minecraft Server消息互通插件",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/17TheWord/nonebot-plugin-mcqq",
    packages=["nonebot_plugin_mcqq"],
    classifiers=[
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Operating System :: OS Independent"
    ],
    install_requires=[
        'nonebot2>=2.1.3',
        'mcqq-tool>=1.0.5',
        'aio-mc-rcon>=3.2.2',
        'nonebot2[httpx]',
        'nonebot2[fastapi]',
        'nonebot2[websockets]',
        'nonebot-adapter-qq>=1.3.5',
        'nonebot-adapter-onebot>=2.3.1',
        'nonebot-adapter-minecraft>=1.0.5',
        'nonebot-plugin-guild-patch>=0.2.3',
    ]
)
