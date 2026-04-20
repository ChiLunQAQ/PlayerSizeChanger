from mcdreforged.api.all import *
import json
import os

# 插件常量
DEFAULT_SIZE = 1.0
BLOCK_SIZE = 0.45
TR_KEY_PREFIX = 'player_size_changer'

class PlayerSizeChanger:
    def __init__(self, server):
        self.server = server
        self.player_sizes = {}
        self.load_player_sizes()
    
    def load_player_sizes(self):
        """从文件加载玩家大小数据"""
        data_path = os.path.join('config', 'player_sizes.json')
        
        if os.path.exists(data_path):
            try:
                with open(data_path, 'r', encoding='utf-8') as f:
                    self.player_sizes.update(json.load(f))
                self.server.logger.info('玩家大小数据加载成功')
            except Exception as e:
                self.server.logger.error(f'加载玩家大小数据时失败: {e}')
    
    def save_player_sizes(self):
        """保存玩家大小数据到文件"""
        data_path = os.path.join('config', 'player_sizes.json')
        os.makedirs('config', exist_ok=True)
        
        try:
            with open(data_path, 'w', encoding='utf-8') as f:
                json.dump(self.player_sizes, f, indent=4, ensure_ascii=False)
            self.server.logger.info('玩家大小数据保存成功')
        except Exception as e:
            self.server.logger.error(f'保存玩家大小数据时失败: {e}')
    
    def set_block_size(self, src):
        """设置玩家大小为方块大小"""
        if not src.is_player:
            self.server.tell(src.player, self.server.rtr(f'{TR_KEY_PREFIX}.messages.player_only'))
            return
        
        player = src.player
        
        # 如果尚未保存原始大小，则保存
        if player not in self.player_sizes:
            self.player_sizes[player] = DEFAULT_SIZE
            self.save_player_sizes()
        
        # 尝试多种属性ID格式以支持不同Minecraft版本
        commands = [
            # 1.21.2+ 版本使用 scale
            f'execute as {player} at @s run attribute @s scale base set {BLOCK_SIZE}',
            # 1.20.5-1.21.1 版本使用 minecraft:generic.scale
            f'execute as {player} at @s run attribute @s minecraft:generic.scale base set {BLOCK_SIZE}',
            # 使用 data merge 命令的 scale 格式
            f'data merge entity @p[name="{player}"] {{Attributes:[{{Name:"scale",Base:{BLOCK_SIZE}}}]}}',
            # 使用 data merge 命令的 generic.scale 格式
            f'data merge entity @p[name="{player}"] {{Attributes:[{{Name:"generic.scale",Base:{BLOCK_SIZE}}}]}}'
        ]
        
        for cmd in commands:
            self.server.execute(cmd)
        
        self.server.tell(player, self.server.rtr(f'{TR_KEY_PREFIX}.messages.block_size_set'))
        self.server.logger.info(f'将 {player} 设置为方块大小')
    
    def restore_original_size(self, src):
        """恢复玩家到原始大小"""
        if not src.is_player:
            self.server.tell(src.player, self.server.rtr(f'{TR_KEY_PREFIX}.messages.player_only'))
            return
        
        player = src.player
        original_size = self.player_sizes.get(player, DEFAULT_SIZE)
        
        # 尝试多种属性ID格式以支持不同Minecraft版本
        commands = [
            # 1.21.2+ 版本使用 scale
            f'execute as {player} at @s run attribute @s scale base set {original_size}',
            # 1.20.5-1.21.1 版本使用 minecraft:generic.scale
            f'execute as {player} at @s run attribute @s minecraft:generic.scale base set {original_size}',
            # 使用 data merge 命令的 scale 格式
            f'data merge entity @p[name="{player}"] {{Attributes:[{{Name:"scale",Base:{original_size}}}]}}',
            # 使用 data merge 命令的 generic.scale 格式
            f'data merge entity @p[name="{player}"] {{Attributes:[{{Name:"generic.scale",Base:{original_size}}}]}}'
        ]
        
        for cmd in commands:
            self.server.execute(cmd)
        
        self.server.tell(player, self.server.rtr(f'{TR_KEY_PREFIX}.messages.original_size_restored'))
        self.server.logger.info(f'将 {player} 恢复到原始大小: {original_size}')
    
    def show_menu(self, src):
        """显示大小更改菜单"""
        if not src.is_player:
            self.server.tell(src.player, self.server.rtr(f'{TR_KEY_PREFIX}.messages.player_only'))
            return
        
        player = src.player
        # 显示菜单文本
        self.server.tell(player, self.server.rtr(f'{TR_KEY_PREFIX}.menu.title'))
        self.server.tell(player, self.server.rtr(f'{TR_KEY_PREFIX}.menu.description'))
        self.server.tell(player, '')
        self.server.tell(player, '【' + self.server.rtr(f'{TR_KEY_PREFIX}.menu.format_title') + '】')
        # 使用正确的RText语法
        self.server.tell(player, RText('!!size').c(RAction.suggest_command, '!!size').h('点击执行命令') + ' 显示帮助信息')
        self.server.tell(player, RText('!!size block').c(RAction.suggest_command, '!!size block').h('点击执行命令') + ' 设置为方块大小 (简写: !!size bl)')
        self.server.tell(player, RText('!!size restore').c(RAction.suggest_command, '!!size restore').h('点击执行命令') + ' 恢复原始大小 (简写: !!size res)')
        self.server.tell(player, '')
        self.server.tell(player, self.server.rtr(f'{TR_KEY_PREFIX}.menu.footer'))

# 全局实例
size_changer = None

def on_load(server, prev):
    """插件加载"""
    global size_changer
    server.logger.info('Player Size Changer 插件已加载!')
    
    # 注册翻译
    lang_dir = os.path.join(os.path.dirname(__file__), '..', 'lang')
    if os.path.exists(lang_dir):
        for file in os.listdir(lang_dir):
            if file.endswith('.json'):
                lang_code = file[:-5]  # 移除 .json 扩展名
                lang_file = os.path.join(lang_dir, file)
                try:
                    with open(lang_file, 'r', encoding='utf-8') as f:
                        translations = json.load(f)
                        server.register_translation(lang_code, translations)
                    server.logger.info(f'已加载 {lang_code} 的翻译')
                except Exception as e:
                    server.logger.error(f'加载 {lang_code} 的翻译时失败: {e}')
    
    # 创建大小更改器实例
    size_changer = PlayerSizeChanger(server)
    
    # 注册命令
    server.register_command(
        Literal('!!size')
        .runs(lambda src: size_changer.show_menu(src))
        .then(Literal('block').runs(lambda src: size_changer.set_block_size(src)))
        .then(Literal('bl').runs(lambda src: size_changer.set_block_size(src)))
        .then(Literal('restore').runs(lambda src: size_changer.restore_original_size(src)))
        .then(Literal('res').runs(lambda src: size_changer.restore_original_size(src)))
    )
    
    # 注册帮助信息
    server.register_help_message('!!size', server.rtr(f'{TR_KEY_PREFIX}.messages.help'))

def on_unload(server):
    """插件卸载"""
    if size_changer:
        size_changer.save_player_sizes()
    server.logger.info('Player Size Changer 插件已卸载!')
