import json

# 读取文件
with open('products.json', 'r', encoding='utf-8') as f:
    # 跳过第一行的表头
    f.readline()
    # 读取JSON数据
    data = f.read().strip()
    surcharges = json.loads(data)

# 更新描述
surcharges[3]['items'][1]['description'] = '如果产品超过70磅，将由Ground服务为送至住宅地址，而非Home服务'

# 保存更新后的SQL语句
with open('update.sql', 'w', encoding='utf-8') as f:
    sql = f"UPDATE products SET surcharges = '{json.dumps(surcharges, ensure_ascii=False)}' WHERE id = 3502;"
    f.write(sql)

print("更新SQL已生成，请检查update.sql文件") 