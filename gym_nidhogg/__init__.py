from gym.envs.registration import register

register(
    id='nidhogg-v0',
    entry_point='gym_nidhogg.envs:NidhoggEnv',
)
# register(
#     id='foo-extrahard-v0',
#     entry_point='gym_foo.envs:FooExtraHardEnv',
# )
