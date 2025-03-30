# 00feudal

## feudal_new_net
* 輸入:
  python "C:\Users\yuhsu\OneDrive\桌面\feudal_new_net\run.py" Build_r --agent feudal --map BuildMarines --envs 3 --res 16 --steps_per_batch 16 --iters 50000 --lr 0.0001 --entropy_weight 0.05 --save_iters 32 --summary_iters 32 --vis --value_loss_weight 0.5 --discount 0.95

  tensorboard --logdir="C:\Users\yuhsu\out\summary\Build_r"
* 得: nan
* max  score: 13


## feudal_new_net(fc)
* 輸入:
  python "C:\Users\yuhsu\OneDrive\桌面\feudal_new_net(fc)\run.py" Build_w --agent feudal --map BuildMarines --envs 3 --res 16 --steps_per_batch 16 --iters 50000 --lr 0.0001 --entropy_weight 0.05 --save_iters 32 --summary_iters 32 --vis --value_loss_weight 0.5 --discount 0.95

  tensorboard --logdir="C:\Users\yuhsu\out\summary\Build_w"
* 得: 50000次之後 ， 非nan (score 還有分數)
* max  score: 16


## 兩者差別
* g_ & convLSTMout 有無經過 RNN (沒經過用fc層替代)


## 其他試驗 feudal_new_net(fc)
* 輸入:python "C:\Users\yuhsu\OneDrive\桌面\feudal_new_net(fc)\run.py" Build_i --agent feudal --map BuildMarines --envs 3 --res 16 --steps_per_batch 16 --iters 50000 --lr 0.01 --entropy_weight 0.05 --save_iters 32 --summary_iters 32 --vis --value_loss_weight 0.5 --discount 0.95

  tensorboard --logdir="C:\Users\yuhsu\out\summary\Build_i"
* 得: 第30回合後，score為0
* max  score: 10
