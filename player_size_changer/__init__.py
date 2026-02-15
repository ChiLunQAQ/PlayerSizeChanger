from mcdreforged.api.all import *
import json
import os

# 默认玩家高度 (1.0 = 正常高度)
DEFAULT_SIZE = 1.0
# 方块高度 (0.45 = 近似方块高度)
BLOCK_SIZE = 0.45

# 存储玩家原始高度
player_sizes = {}

# 翻译键前缀
TR_KEY_PREFIX = 'player_size_changer'

class PlayerSizeChanger:
    def __init__(self, server):
        self.server = server
        self.load_player_sizes()
    
    def load_player_sizes(self):
        """从文件加载玩家高度"""
        global player_sizes
        data_path = os.path.join('config', 'player_sizes.json')
        
        if os.path.exists(data_path):
            try:
                with open(data_path, 'r', encoding='utf-8') as f:
                    player_sizes.update(json.load(f))
                self.server.logger.info('玩家高度加载成功')
            except Exception as e:
                self.server.logger.error(f'加载玩家高度时失败: {e}')
    
    def save_player_sizes(self):
        """保存玩家高度到文件"""
        data_path = os.path.join('config', 'player_sizes.json')
        os.makedirs('config', exist_ok=True)
        
        try:
            with open(data_path, 'w', encoding='utf-8') as f:
                json.dump(player_sizes, f, indent=4, ensure_ascii=False)
            self.server.logger.info('玩家高度保存成功')
        except Exception as e:
            self.server.logger.error(f'保存玩家高度时失败: {e}')
    
    def set_block_size(self, src):
        """设置玩家高度为方块高度"""
        if not src.is_player:
            src.reply(src.get_server().rtr(f'{TR_KEY_PREFIX}.messages.player_only'))
            return
        
        player = src.player
        
        # 如果尚未保存原始高度，则保存
        if player not in player_sizes:
            player_sizes[player] = DEFAULT_SIZE
            self.save_player_sizes()
        
        # 使用 attribute 命令 (Minecraft 1.16+)
        self.server.execute(f'execute as {player} at @s run attribute @s minecraft:generic.scale base set {BLOCK_SIZE}')
        self.server.execute(f'tellraw {player} {{"translate":"commands.attribute.base_value.set.success","with":[{{"translate":"attribute.name.generic.scale"}},"{player}","{BLOCK_SIZE}"]}}')
        src.reply(self.server.rtr(f'{TR_KEY_PREFIX}.messages.block_size_set'))
        self.server.logger.info(f'将 {player} 设置为方块高度')
    
    def restore_original_size(self, src):
        """恢复玩家到原始高度"""
        if not src.is_player:
            src.reply(src.get_server().rtr(f'{TR_KEY_PREFIX}.messages.player_only'))
            return
        
        player = src.player
        
        # 获取原始高度或使用默认值
        original_size = player_sizes.get(player, DEFAULT_SIZE)
        
        # 使用 attribute 命令 (Minecraft 1.16+)
        self.server.execute(f'execute as {player} at @s run attribute @s minecraft:generic.scale base set {original_size}')
        self.server.execute(f'tellraw {player} {{"translate":"commands.attribute.base_value.set.success","with":[{{"translate":"attribute.name.generic.scale"}},"{player}","{original_size}"]}}')
        src.reply(self.server.rtr(f'{TR_KEY_PREFIX}.messages.original_size_restored'))
        self.server.logger.info(f'将 {player} 恢复到原始高度: {original_size}')
    
    def show_menu(self, src):
        """显示高度更改菜单"""
        if not src.is_player:
            src.reply(src.get_server().rtr(f'{TR_KEY_PREFIX}.messages.player_only'))
            return
        
        player = src.player
        # 获取服务器实例用于翻译
        server = src.get_server()
        
        # 获取翻译后的菜单文本
        menu_text = [
            server.rtr(f'{TR_KEY_PREFIX}.menu.title'),
            server.rtr(f'{TR_KEY_PREFIX}.menu.description'),
            '',
            '【' + server.rtr(f'{TR_KEY_PREFIX}.menu.format_title') + '】',
            server.rtr(f'{TR_KEY_PREFIX}.menu.command_help'),
            server.rtr(f'{TR_KEY_PREFIX}.menu.command_block'),
            server.rtr(f'{TR_KEY_PREFIX}.menu.command_restore'),
            '',
            server.rtr(f'{TR_KEY_PREFIX}.menu.footer')
        ]
        
        for line in menu_text:
            src.reply(line)
        
        # 设置菜单状态为 false，因为不再使用交互式菜单
        # 命令将通过命令树直接处理
        menu_state[player] = False

# 全局实例
size_changer = None

# 存储菜单状态
menu_state = {}

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
        .then(Literal('restore').runs(lambda src: size_changer.restore_original_size(src)))
    )
    
    # 注册帮助信息
    server.register_help_message('!!size', lambda server: server.rtr(f'{TR_KEY_PREFIX}.messages.help'))

def on_user_info(server, info):
    """处理用户输入（不再用于菜单）"""
    # 菜单不再是交互式的，命令通过命令树处理
    pass

def on_unload(server):
    """插件卸载"""
    if size_changer:
        size_changer.save_player_sizes()
    server.logger.info('Player Size Changer 插件已卸载!')
