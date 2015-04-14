MONGODB写入速度1000条/秒

4 个进程guba_stock_list_redis_spider 1个入口按股票分collection 1540 /min
15个进程guba_stock_detail_redis_spider 1个入口按股票分collection 1990 /min

100以上的15只，50-100之间的78只

24核100GB内存机器 每个scrapy进程占用内存0.1%=100MB, CPU: 2.2%

15 stocks, 每2分钟更新一次
    单个mongodb集群 3台爬虫机器 每台机器1个scrapy_detail 1个scrapy_list list速度3条/分钟 detail速度3条/分钟
    单个mongodb集群 3台爬虫机器 每台机器3个scrapy_detail 1个scrapy_list list速度3条/分钟 detail速度3条/分钟
    单个mongodb集群 3台爬虫机器 每台机器3个scrapy_detail 3个scrapy_list list速度3条/分钟 detail速度3条/分钟

30 stocks，每2分钟更新一次
    单个mongodb集群 3台爬虫机器 每台机器3个scrapy_detail 3个scrapy_list list速度6条/分钟 detail速度6条/分钟
    单个mongodb集群 3台爬虫机器 每台机器6个scrapy_detail 3个scrapy_list list速度6条/分钟 detail速度6条/分钟

60 stocks，每2分钟更新一次
    单个mongodb集群 3台爬虫机器 每台机器6个scrapy_detail 3个scrapy_list list速度10条/分钟 detail速度10条/分钟

90 stocks，每2分钟更新一次
    单个mongodb集群 3台爬虫机器 每台机器6个scrapy_detail 3个scrapy_list list速度10条/分钟 detail速度10条/分钟
    单个mongodb集群 3台爬虫机器 每台机器9个scrapy_detail 4个scrapy_list list速度条10/分钟 detail速度10条/分钟

2552 stocks, 每2分钟更新一次
    单个mongodb集群 3台爬虫机器 每台机器20个scrapy_detail 10个scrapy_list list速度条280/分钟 detail速度220条/分钟

MONGODB存储股吧帖子数据规模估计：
  存储量与空间换算：40GB=3000万 => 每1万条帖子= 13.653MB => 每条帖子1.4KB
  每天发帖量估计：2500只股票每天发布4万条帖子 => 每年 365 * 4万 = 1460万 => 每年存储量 1500 * 13.653 MB = 20GB => 1万只股票每年存储增长100GB

增量爬虫节点：3个，每个配置如下：
  cat /proc/cpuinfo | grep name | cut -f2 -d: | uniq -c
      Intel(R) Xeon(R) CPU E5-2640 v2 @ 2.00GHz 32逻辑CPU
  cat /proc/cpuinfo | grep physical | uniq -c
      2个unique physical id, 2个8核CPU
  CPU: Intel(R) Xeon(R) CPU E5-2640 v2 @ 2.00GHz 32逻辑CPU, 内存：100GB
  2500支股票实现时滞为两分钟、频率为1分钟1次的帖子爬取与情绪计算，需要配置3台服务器，共计100个进程，每台服务器CPU负载为4(4%),内存占用30GB(30%)

实现10000支股票时滞为两分钟、频率为1分钟1次的帖子爬取与情绪计算，需配置6台服务器，共计400个进程，每台服务器CPU负载10%，内存占用60%
