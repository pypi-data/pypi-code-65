def dataset_split_train_test(dataset,split_size):
	train_size=int(len(dataset)*split_size)
	test_size=len(dataset)-train_size
	train,test=dataset[0:train_size],dataset[train_size:len(dataset)]
	return train,test