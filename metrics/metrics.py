import torch
import numpy as np
from config.configurator import configs

class Metric(object):
    def __init__(self):
        self.metrics = configs['test']['metrics']
        self.k = configs['test']['k']

    def recall(self, test_data, r, k):
        right_pred = r[:, :k].sum(1)
        recall_n = np.array([len(test_data[i]) for i in range(len(test_data))])
        recall = np.sum(right_pred / recall_n)
        return recall

    def precision(self, r, k):
        right_pred = r[:, :k].sum(1)
        precis_n = k
        precision = np.sum(right_pred) / precis_n
        return precision


    def mrr(self, r, k):
        pred_data = r[:, :k]
        scores = np.log2(1. / np.arange(1, k + 1))
        pred_data = pred_data / scores
        pred_data = pred_data.sum(1)
        return np.sum(pred_data)


    def ndcg(self, test_data, r, k):
        assert len(r) == len(test_data)
        pred_data = r[:, :k]

        test_matrix = np.zeros((len(pred_data), k))
        for i, items in enumerate(test_data):
            length = k if k <= len(items) else len(items)
            test_matrix[i, :length] = 1
        max_r = test_matrix
        idcg = np.sum(max_r * 1. / np.log2(np.arange(2, k + 2)), axis=1)
        dcg = pred_data * (1. / np.log2(np.arange(2, k + 2)))
        dcg = np.sum(dcg, axis=1)
        idcg[idcg == 0.] = 1.
        ndcg = dcg / idcg
        ndcg[np.isnan(ndcg)] = 0.
        return np.sum(ndcg)

    def get_label(self, test_data, pred_data):
        r = []
        for i in range(len(test_data)):
            ground_true = test_data[i]
            predict_topk = pred_data[i]
            pred = list(map(lambda x: x in ground_true, predict_topk))
            pred = np.array(pred).astype("float")
            r.append(pred)
        return np.array(r).astype('float')

    def eval_batch(self, data, topks):
        sorted_items = data[0].numpy()
        ground_true = data[1]
        r = self.get_label(ground_true, sorted_items)

        result = {}
        for metric in self.metrics:
            result[metric] = []

        for k in topks:
            for metric in result:
                if metric == 'recall':
                    result[metric].append(self.recall(ground_true, r, k))
                if metric == 'ndcg':
                    result[metric].append(self.ndcg(ground_true, r, k))
                if metric == 'precision':
                    result[metric].append(self.precision(r, k))
                if metric == 'mrr':
                    result[metric].append(self.mrr(r, k))

        for metric in result:
            result[metric] = np.array(result[metric])

        return result

    def eval(self, model, test_dataloader):
        result = {}
        for metric in self.metrics:
            result[metric] = np.zeros(len(self.k))

        batch_ratings = []
        ground_truths = []
        test_user_count = 0
        test_user_num = len(test_dataloader.test_users)
        for _, tem in enumerate(test_dataloader):
            # predict result
            batch_data = list(map(lambda x: x.long().cuda()), tem)
            batch_pred = model.full_predict(batch_data)
            test_user_count += batch_rate.shape[0]
            _, batch_rate = torch.topk(batch_pred, k=max(self.k))
            batch_ratings.append(batch_rate)

            # ground truth
            ground_truth = []
            test_user = tem[0].numpy().tolist()
            for user_idx in test_user:
                ground_truth.append(list(test_dataloader.user_pos_lists[user_idx]))
            ground_truths.append(ground_truth)
        assert test_user_count == test_user_num

        # calculate metrics
        data_pair = zip(batch_ratings, ground_truths)
        eval_results = []
        for _data in data_pair:
            eval_results.append(self.eval_batch(_data, self.k))
        for metric in self.metrics:
            result[metric] += eval_results[metric] / test_user_num

        return result







